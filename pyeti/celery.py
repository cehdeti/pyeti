from celery import shared_task, subtask, group


@shared_task
def distributed_map(it, task):
    """
    Chain together a task that returns a list and another task that is applied
    to each element in the list. For example:

            @shared_task
            def get_items():
                return (i for i in range(10))

            @shared_task
            def print_item(item):
                print(item)

            get_items.si() | distributed_map.s(print_item.s())
    """
    return group(subtask(task).clone(args=i) for i in it)()
