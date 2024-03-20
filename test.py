import fuzzywuzzy
import fuzzywuzzy.fuzz


match_rate = fuzzywuzzy.fuzz.ratio("某幻君","某幻君/阿达娃/杨秋儒")
print(match_rate)