import fuzzywuzzy
import fuzzywuzzy.fuzz


match_rate = fuzzywuzzy.fuzz.ratio("甜約翰 Sweet John","甜約翰")
print(match_rate)