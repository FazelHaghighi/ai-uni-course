from colorama import Fore, Style

class Task:
    def __init__(self, name, start_time, end_time, resources, priority, dependencies=None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.resources = resources
        self.priority = priority
        self.dependencies = dependencies or []
        self.assigned = False
        self.assigned_time = None

class Resource:
    def __init__(self, name):
        self.name = name
        self.schedule = set()

    def is_available(self, start, duration=1):
        return all(time not in self.schedule for time in range(start, start + duration))

    def assign(self, task, start):
        self.schedule.update(range(start, start + 1))

def can_schedule(task, start, resources):
    if not (task.start_time <= start < task.end_time):
        return False
    if not all(resources[resource].is_available(start) for resource in task.resources):
        return False
    if any(not (dependency.assigned and dependency.assigned_time + 1 <= start) for dependency in task.dependencies):
        return False
    return True

def schedule_task(task, start, resources):
    for resource_name in task.resources:
        resources[resource_name].assign(task, start)
    task.assigned = True
    task.assigned_time = start

def backtrack(tasks, resources, time=0):
    if all(task.assigned for task in tasks):
        return True

    for task in (t for t in tasks if not t.assigned):
        for start in range(task.start_time, task.end_time + 1):
            if can_schedule(task, start, resources):
                schedule_task(task, start, resources)
                if backtrack(tasks, resources, time + 1):
                    return True
                task.assigned = False
                task.assigned_time = None
                for resource_name in task.resources:
                    resources[resource_name].schedule.remove(start)
    return False

def print_task_schedule(tasks):
    print(Fore.GREEN + Style.BRIGHT + "Task Schedule:" + Style.RESET_ALL)
    for task in tasks:
        print(f"{Fore.CYAN}Task {task.name} is scheduled to start at time {task.assigned_time}{Style.RESET_ALL}")

def print_failure_message():
    print(Fore.RED + "Failed to schedule all tasks." + Style.RESET_ALL)

def main():
    # Example tasks and resources
    tasks = [
        Task("Report Delivery", 1, 15, ["Researcher 1", "Writer 1"], "High"),
        Task("Application Programming", 5, 25, ["Programmer 1", "UI Designer 1"], "Medium"),
        Task("Testing and Debugging", 20, 32, ["Tester 1"], "Low")
    ]

    resources = {name: Resource(name) for name in ["Researcher 1", "Writer 1", "Programmer 1", "UI Designer 1", "Tester 1"]}

    # Define dependencies (Testing and Debugging depends on Application Programming)
    tasks[2].dependencies.append(tasks[1])

    # Sort tasks based on priority
    tasks.sort(key=lambda t: t.priority, reverse=True)

    # Run backtracking algorithm to schedule tasks
    if backtrack(tasks, resources):
        print_task_schedule(tasks)
    else:
        print_failure_message()

if __name__ == "__main__":
    main()
