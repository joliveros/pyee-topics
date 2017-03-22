# -*- coding: utf-8 -*-

from pytest import raises
from mock import Mock
from pyee import EventEmitter, PatternException


def test_is_pattern():
    ee = EventEmitter()
    assert ee._isPattern('a/#')
    assert ee._isPattern('a/+/+')
    assert not ee._isPattern('a/#/+')
    assert not ee._isPattern('a/c+/c')
    assert not ee._isPattern('a/#/c')


def test_pattern_matching():
    """Test that patterns are correctly interpreted"""
    ee = EventEmitter()
    assert ee._matches('#', 'a/b/c')
    assert ee._matches('+/b/c', 'a/b/c')
    assert ee._matches('a/#', 'a/b/c')
    assert not ee._matches('a/#', 'c/a/b/c')
    with raises(PatternException) as e:
        ee._matches('#/b/c', 'c')
    assert not ee._matches('a/+/d/e', 'a/b/c/d/e')


def test_matching_topic():
    """Test that a pattern can be passed as an event"""

    ee = EventEmitter()
    call_me = Mock()

    @ee.on('event/+/ok', call_me)
    def event_handler(data, **kwargs):
        call_me()

    ee.emit('event/first/ok')

    ee.emit('event/second/ok')

    ee.emit('event/first/ok2')

    assert call_me.call_count == 3


def test_shorter_pattern():
    """Tests correct behaviour with shorter patterns"""

    ee = EventEmitter()
    call_me = Mock()

    @ee.on('#')
    def event_handler(ev):
        call_me()

    ee.emit('a/b/c')

    ee.emit('cool')

    assert call_me.call_count == 2


def test_longer_pattern():
    """Tests correct behaviour with longer patterns"""

    ee = EventEmitter()
    call_me = Mock()

    @ee.on('a/b/#')
    def event_handler(ev):
        call_me()

    ee.emit('c')
    ee.emit('c')

    call_me.assert_not_called()
