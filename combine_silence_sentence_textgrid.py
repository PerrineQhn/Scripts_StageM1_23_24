from praatio import tgio
import textgrid

# NE PAS SUPPRIMER CETTE FONCTION
def create_tier(ipus_path, tokens_path, output_path):
    textgrid_ipus = tgio.openTextgrid(ipus_path)
    textgrid_tokens = tgio.openTextgrid(tokens_path)

    textgrid = tgio.Textgrid()

    combine_intervals = []

    # Access specific tiers
    ipus_tier = textgrid_ipus.tierDict['IPUs']
    tokens_tier = textgrid_tokens.tierDict['TokensAlign']

    ipus_intervals = ipus_tier.entryList
    tokens_intervals = tokens_tier.entryList

    # Store the last end time of the silence to adjust the start of the next token
    last_silence_end = 0
    for token_start, token_end, token_label in tokens_intervals:
        # Check if the token starts after the last silence ended
        if token_start >= last_silence_end:
            overlapped = False
            # Check each silence interval
            for ipu_start, ipu_end, ipu_label in ipus_intervals:
                if ipu_label == '#' and not (token_end <= ipu_start or token_start >= ipu_end):
                    # If token starts before the silence and ends after the silence starts
                    if token_start < ipu_start < token_end:
                        combine_intervals.append([token_start, ipu_start, token_label])
                    # If token starts before the silence ends and ends after the silence
                    if token_start < ipu_end < token_end:
                        # Adjust the start for next potential token
                        token_start = ipu_end
                    overlapped = True
            # If token was not overlapped by silence or only partially overlapped
            if not overlapped or token_start < token_end:
                combine_intervals.append([token_start, token_end, token_label])
            # Update the last silence end time
            last_silence_end = token_start
        else:
            # If the token starts before the last silence ended, adjust the token start
            if token_end > last_silence_end:
                combine_intervals.append([last_silence_end, token_end, token_label])
                last_silence_end = token_end  # Update the last silence end time

    # Create the combined tier
    tier = tgio.IntervalTier("Combined", combine_intervals, minT=tokens_intervals[0][0], maxT=tokens_intervals[-1][1])
    textgrid.addTier(tier)
    textgrid.save(output_path)



def find_phrases_with_hash(textgrid_path, ipus_textgrid_path):
    # Charger les fichiers .TextGrid et .ipus.TextGrid
    textgrid = tgio.openTextgrid(textgrid_path)
    ipus_textgrid = tgio.openTextgrid(ipus_textgrid_path)

    # Récupérer les intervalles avec "#" dans ipus.TextGrid
    ipus_intervals_with_hash = []
    for interval in ipus_textgrid.tierDict["IPUs"].entryList:
        if interval[2] == "#":
            ipus_intervals_with_hash.append((interval[0], interval[1]))

    # Récupérer les phrases correspondantes dans .TextGrid
    phrases_with_hash = []
    for ipus_interval in ipus_intervals_with_hash:
        ipus_xmin, ipus_xmax = ipus_interval

        # Chercher la phrase correspondante dans .TextGrid
        for textgrid_interval in textgrid.tierDict["trans"].entryList:
            textgrid_xmin, textgrid_xmax = textgrid_interval[:2]

            if textgrid_xmin <= ipus_xmin <= textgrid_xmax and textgrid_xmin <= ipus_xmax <= textgrid_xmax:
                # La phrase .TextGrid correspond à l'intervalle ipus.TextGrid
                phrases_with_hash.append(textgrid_interval[2])

    # Retourner les phrases correspondantes
    return phrases_with_hash

# Utilisation de la fonction
textgrid_path = "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M.TextGrid"
ipus_textgrid_path = "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-ipus.TextGrid"
id_textgrid_path = "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-id.TextGrid"
# phrases = find_phrases_with_hash(textgrid_path, ipus_textgrid_path)

create_tier(ipus_textgrid_path, id_textgrid_path, "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-syl_tok.TextGrid")


# # Afficher les phrases correspondantes
# for phrase in phrases:
#     print(phrase)