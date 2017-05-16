from piper_driver.addins.queue import Queue


def test_first(redis):
    Queue.push('q1', '1')
    Queue.push('q2', '1')
    Queue.push('q1', '2')
    Queue.push('q2', '2')
    Queue.push('q1', '3')
    Queue.push('q2', '3')
    Queue.push('q1', '4')
    Queue.push('q2', '4')
    assert Queue.pop('q1') == '1'
    assert Queue.pop('q1') == '2'
    assert Queue.pop('q1') == '3'
    assert Queue.pop('q1') == '4'
    assert Queue.pop('q1') is None
    assert Queue.pop('q2') == '1'
    assert Queue.pop('q2') == '2'
    assert Queue.pop('q2') == '3'
    assert Queue.pop('q2') == '4'
    assert Queue.pop('q2') is None
