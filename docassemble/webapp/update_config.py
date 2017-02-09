import sys
if __name__ == "__main__":
    import docassemble.base.config
    docassemble.base.config.load(arguments=sys.argv)

def check_for_config():
    from docassemble.base.config import s3_config, S3_ENABLED, daconfig
    if S3_ENABLED:
        import docassemble.webapp.amazon
        s3 = docassemble.webapp.amazon.s3object(s3_config)
        key = s3.get_key('config.yml')
        if key.exists():
            key.get_contents_to_filename(daconfig['config file'])

if __name__ == "__main__":
    check_for_config()

            

