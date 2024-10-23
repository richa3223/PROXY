from lambdas.utils.aws.start_glue_crawler import StartGlueCrawler

start_glue_crawler = StartGlueCrawler()


def lambda_handler(event, context):
    """Lambda handler function for starting the standard audit data crawler
    when a new folder gets added to the standard audit events bucket

    Args:
        event (dict):
        context (dict): Current context

    Returns:
        dict:   AWS response of the "gluel:StartCrawler" operation
    """
    return start_glue_crawler.main(event, context)
