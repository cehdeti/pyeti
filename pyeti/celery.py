from celery import shared_task, subtask, group, signature


@shared_task
def distributed_map(it, task, end_task=None):
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
    grp = group(subtask(task).clone(args=arg) for arg in it)

    if end_task:
        end_task = signature(end_task)
        return (grp | end_task)()
    else:
        return grp()
