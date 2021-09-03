def pytest_addoption(parser):
    parser.addoption(
        '--amplify_token',
        default=False,
        help='token of amplify'
    )
