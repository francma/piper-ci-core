from piper_core.container import Container


def test_first(container: Container):
    queue = container.get_queue()
    queue.push('q1', '1')
    queue.push('q2', '1')
    queue.push('q1', '2')
    queue.push('q2', '2')
    queue.push('q1', '3')
    queue.push('q2', '3')
    queue.push('q1', '4')
    queue.push('q2', '4')
    assert queue.pop('q1') == '1'
    assert queue.pop('q1') == '2'
    assert queue.pop('q1') == '3'
    assert queue.pop('q1') == '4'
    assert queue.pop('q1') is None
    assert queue.pop('q2') == '1'
    assert queue.pop('q2') == '2'
    assert queue.pop('q2') == '3'
    assert queue.pop('q2') == '4'
    assert queue.pop('q2') is None
