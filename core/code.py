# Task status code
TASK_COMPLETED = 0       # Task execution completed (possibly timeout)
TASK_SUCCESS = 1         # Task successfully completed without timeout
TASK_NNPE = 41           # NetworkXNoPathError
TASK_NCGE = 42           # NetCongestionError
TASK_IBFE = 43           # InsufficientBufferError
TASK_NOFE = 44           # NodeOfflineError
TASK_NNFE = 45           # NodeNotFoundError
TASK_TOTE = 46           # TimeoutError
