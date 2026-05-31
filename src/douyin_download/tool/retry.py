from douyin_download.config.constant import RETRY_ACCOUNT


def retry(function):
    '''发生错误时尝试重新执行'''
    def inner(*args, **kwargs):
        for _ in range(int(RETRY_ACCOUNT) + 1):
            if result := function(*args, **kwargs):
                return result
        return result

    return inner
