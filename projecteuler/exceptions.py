class NeedRedirection(Exception):
    """
    When user passed invalid query parameters throw address bar,
    redirect him to the same page without query parameters
    """
