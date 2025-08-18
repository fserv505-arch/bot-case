import os
import traceback

# Configure environment for a single scrape run
os.environ.setdefault('SEARCH_URL', 'https://bostad.blocket.se/en/find-home?maxMonthlyCost=11500&searchAreas=Stockholm~~se&sharedHome=privateHome')
os.environ.setdefault('APP_DIR', 'C\\app')

try:
    import main
    main.scrape_qasa()
except Exception:
    traceback.print_exc()



