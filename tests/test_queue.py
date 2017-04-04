from piper_driver.addins.queue import Queue


def test_first(redis):
    queue1 = Queue('test')
    queue2 = Queue('test2')
    queue1.push('1')
    queue2.push('1')
    queue1.push('2')
    queue2.push('2')
    queue1.push('3')
    queue2.push('3')
    queue1.push('4')
    queue2.push('4')
    assert queue1.pop() == '1'
    assert queue1.pop() == '2'
    assert queue1.pop() == '3'
    assert queue1.pop() == '4'
    assert queue1.pop() is None
    assert queue2.pop() == '1'
    assert queue2.pop() == '2'
    assert queue2.pop() == '3'
    assert queue2.pop() == '4'
    assert queue2.pop() is None
