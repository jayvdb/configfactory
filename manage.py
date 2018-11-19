from configfactory import cli
from configfactory.support import env

if __name__ == '__main__':

    # Set development default variables
    env.set_development_defaults()

    # Run CLI
    cli.main()
