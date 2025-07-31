# -*- coding: utf-8 -*-

BOT_NAME = 'scraper'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 0.5  # Reduced delay
RANDOMIZE_DOWNLOAD_DELAY = True

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'scraper.pipelines.ValidationPipeline': 100,
    'scraper.pipelines.CleaningPipeline': 200,
    'scraper.pipelines.OptimizedImagePipeline': 300,  # Using optimized pipeline
    'scraper.pipelines.DuplicatesPipeline': 400,
}

# Retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 2  # Reduced retry times
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Cache configuration
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [404, 500, 502, 503, 504]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Log configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'scraping.log'

# Timeout configuration
DOWNLOAD_TIMEOUT = 30  # Reduced timeout

# Memory usage
MEMUSAGE_ENABLED = True
MEMUSAGE_WARNING_MB = 512

# Redirections
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 3  # Reduced max redirects

# Enable cookies and compression
COOKIES_ENABLED = True
COMPRESSION_ENABLED = True

# DNS cache
DNSCACHE_ENABLED = True

# Enable AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0

# Disable some unused middlewares
DOWNLOADER_MIDDLEWARES.update({
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': None,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': None,
})

# Feed export
FEED_EXPORT_ENCODING = 'utf-8'
FEED_EXPORT_INDENT = 2
