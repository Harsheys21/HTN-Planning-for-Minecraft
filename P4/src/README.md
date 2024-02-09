The heuristics we chose were:

    1. If a tool was being made, we checked if the same tool
        was being made for a second time.  This was achieved by 
        comparing the current task and the stack of tasks and seeing
        if there were 2 or more cases of making the same tool.  If yes
        we returned True to prune the branch
    
    2. We ensured that the depth limit was set to 65. Essentially what 
        this does it ensure that the tree isn't searching through the 
        branch for too long. It essentially prunes that branch if it's 
        goes too deep

    3. We add a conditional that terminates the program if we run out of time
    
        