from flopt import env
from flopt.env import setup_logger

def test_setLogLevel_DEBUG():
    env.setLogLevel(10)

def test_setLogLevel_DEBUG():
    env.setLogLevel('DEBUG')

def test_setLogLevel_INFO():
    env.setLogLevel(20)

def test_setLogLevel_INFO():
    env.setLogLevel('INFO')

def test_setLogLevel_WARNING():
    env.setLogLevel(30)

def test_setLogLevel_WARNING():
    env.setLogLevel('WARNING')

def test_setLogLevel_ERROR():
    env.setLogLevel(40)

def test_setLogLevel_ERROR():
    env.setLogLevel('ERROR')

def test_setLogLevel_CRITICAL():
    env.setLogLevel(50)

def test_setLogLevel_CRITICAL():
    env.setLogLevel('CRITICAL')

def test_setup_logger():
    setup_logger(__name__)