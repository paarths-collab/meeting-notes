from typing import Optional, Dict, Any
import json
import os
from backend.services.mem0_service import Mem0Service
from backend.services.llm_service import GeminiLLMService

class MeetingQueryAgent:
    """
    Agent that orchestrates meeting queries.
    It can decide to search memory (Mem0) or answer directly.
    """
    
    def __init__(self, llm_service: GeminiLLMService, mem0_service: Mem0Service):
        self.llm = llm_service
        self.mem0 = mem0_service
        
    def run(self, query: str, user_id: str, filters: Optional[Dict[str, Any]] = None) -> (str, list[str]):
        """
        Run the agent for a user query.
        Returns: answer (str), sources (list[str])
        """
        
        # Step 1: Decide if we need to search memory
        # For now, we assume ANY question about meetings requires search.
        # But we can let the LLM refine the search query?
        # A simple ReAct pattern: 
        # "User asked: {query}. To answer this, should I search for specific keywords? 
        # Output SEARCH: <keywords> or ANSWER: <text>"
        
        decision_prompt = f"""
        You are an intelligent assistant. The user asked: "{query}"
        
        Your task is to decide if you need to search past meeting records to answer this.
        
        - If the user is just saying "hi", "thanks", or general chit-chat, reply directly.
        - If the user asks to "Summarize", "Recap", or "Give an overview" of the meeting, use SUMMARY.
        - If the user tests to find specific information (tasks, advice, names), use SEARCH.
        
        CRITICAL SEARCH INSTRUCTIONS:
        - Generate a search query that focuses on KEYWORDS and ENTITIES (e.g. names, topics). 
        - DO NOT use full questions like "What did Amr advise?".
        - KEEP IT CONCISE. Avoid adding too many synonyms unless necessary.
        
        Examples:
        User: "What did Amr advise?" -> SEARCH: Amr advice
        User: "Summarize the meeting" -> SUMMARY
        User: "Key takeaways" -> SUMMARY
        
        Return ONLY one of the following formats:
        SEARCH: <optimized keyword query>
        SUMMARY
        ANSWER: <direct response>
        """
        
        try:
            decision = self.llm.generate(decision_prompt).strip()
        except Exception as e:
            # Fallback to search if decision fails
            print(f"⚠️ Agent decision failed: {e}. Defaulting to search.")
            decision = f"SEARCH: {query}"
            
        # Log decision for debugging
        try:
            with open("backend/agent.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- New Query ---\nUser: {query}\nAgent Decision: {decision}\n")
        except Exception as e:
            print(f"Failed to log agent decision: {e}")
            
        sources = []
        context = ""
        
        if decision == "SUMMARY":
            print("🤖 Agent detected SUMMARY intent.")
            # Use get_all_memories to fetch recent context directly (skipping vector search).
            # This works for both filtered (specific meeting) and unfiltered (all recent) cases.
            print(f"   Fetching recent memories (Limit 20, Filters: {filters})")
            memories = self.mem0.get_all_memories(
                user_id=user_id,
                filters=filters,
                limit=20
            )

        elif decision.startswith("SEARCH:"):
            search_query = decision.replace("SEARCH:", "").strip()
            print(f"🤖 Agent decided to search for: '{search_query}'")
            
            # Execute Tool: Mem0 Search (vector)
            memories = self.mem0.search_memory(
                query=search_query,
                user_id=user_id,
                filters=filters,
                limit=5
            )
            
            # --- Keyword Fallback Logic ---
            # If explicit name "Amr" or other capitalized entities are in query, ensure we find them.
            # This handles cases where vector search misses specific entities.
            keywords = [w for w in search_query.split() if w[0].isupper() and len(w) > 2] # Simple heuristic
            if keywords:
                print(f"🔍 DEBUG: Keyword Fallback for: {keywords}")
                all_memories = self.mem0.get_all_memories(user_id=user_id)
                found_count = 0
                for mem in all_memories:
                    # mem is string (handled by get_all_memories)
                    if any(k.lower() in mem.lower() for k in keywords):
                        if mem not in memories:
                            memories.append(mem)
                            found_count += 1
                if found_count > 0:
                    print(f"✅ Keyword Fallback added {found_count} memories.")
            
        elif decision.startswith("ANSWER:"):
            answer = decision.replace("ANSWER:", "").strip()
            return answer, []
            
        else:
             # Fallback
             return "I didn't understand that request.", []

        if not memories:
            return "I couldn't find any relevant meeting information matching your request.", []
            
        # Prepare context (De-duplicate)
        memories = list(set(memories))
        context = "\n\n---\n\n".join(memories)
            
        # Extract sources
        for mem in memories:
            if "Meeting:" in mem:
                title_line = mem.split("\n")[0]
                title = title_line.replace("Meeting:", "").strip()
                if title and title not in sources:
                    sources.append(title)
                        
        # Step 2: Generate Final Answer
            final_prompt = f"""
            You are an expert meeting assistant.
            User Question: {query}
            
            Relevant Meeting Context found:
            {context}
            
            Instructions:
            1. Answer the question comprehensively based on the context.
            2. Interpret "advice", "suggestions", "action items" as implied advice.
            3. If context doesn't fully answer it, say what you found and what is missing.
            4. Be professional but conversational.
            5. FORMATTING: Do NOT use markdown bullets (*) or bold (**). Use numbered lists (1., 2.) or paragraphs. Keep it clean.
            6. CRITICAL: If the context contains information from DIFFERENT meetings or UNRELATED topics (e.g. Finance vs Cooking), SEPARATE them clearly in your answer. Do not mix them.
            """
            
            answer = self.llm.generate(final_prompt)
            return answer, sources
            

