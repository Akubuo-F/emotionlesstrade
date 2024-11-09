class ViewDefaultLatestCOTReportUseCase:
    """
    View the default version of the latest COT report which contains the data about the open interest, position of commercial and 
    non commercial traders and changes from the previous week report.
    """

    def execute(self, assets) -> list:
        # retrive the latest COT report of the given assets
        # returns a list of default COT reports
        ...