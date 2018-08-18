from configfactory import cli
from configfactory.support import appenv

appenv.set_env_development_defaults()

if __name__ == '__main__':
    cli.main()
