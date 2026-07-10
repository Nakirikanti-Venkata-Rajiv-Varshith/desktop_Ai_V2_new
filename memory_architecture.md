                    User
                      │
                      ▼
           ConversationManager
                      │
                      ▼
              TurnAnalyzer
                      │
               TurnAnalysis
                      │
                      ▼
                 Planner
                      │
                 TaskPlan
                      │
                      ▼
                 Executor
                      │
              ExecutionEvent
                      │
                      ▼
               MemoryManager
      ┌─────────┬─────────┬─────────┬──────────┬──────────┬────────────┐
      │         │         │         │          │          │
      ▼         ▼         ▼         ▼          ▼          ▼
   Entity   Preference Workflow Behavior  Episodic   Semantic
   Memory     Memory    Memory   History   Memory     Memory
      │         │         │         │          │          │
      └─────────┴─────────┴─────────┴──────────┴──────────┘
                              │
                              ▼
                     Long-Term Learning