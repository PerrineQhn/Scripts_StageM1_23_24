import csv
import glob
from tqdm import tqdm


def extract_values_from_text_file(file_content, align_begin, align_end):
    valeurs_correspondantes = []
    nombres_correspondants = []

    for ligne in file_content:
        if "number =" in ligne:
            nombre = float(ligne.split('=')[1])
        elif "value =" in ligne:
            valeur = float(ligne.split('=')[1])
            if align_begin <= nombre <= align_end:
                valeurs_correspondantes.append(valeur)
                nombres_correspondants.append(nombre)

    return valeurs_correspondantes, nombres_correspondants


def extract_points_values_from_tsv(tsv_file_path, text_files_directory, output_directory=None):
    # Ouvrir le fichier TSV contenant les données
    with open(tsv_file_path, 'r') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        # Parcourir chaque ligne du fichier TSV
        for idx, row in tqdm(enumerate(reader), total=90130, bar_format="{l_bar}{bar:10}{r_bar}"):
            file_name = row['File']
            id_T1 = row["ID"]
            form = row['Form']

            data = []
            t1_align_begin_values = []
            t1_align_end_values = []

            # Extraire les valeurs d'alignement pour chaque syllabe T1
            for i in range(1, 9):
                align_begin_key = f'Syl{i}AlignBegin'
                align_end_key = f'Syl{i}AlignEnd'
                if align_begin_key in row and row[align_begin_key] != "_":
                    t1_align_begin_values.append(float(row[align_begin_key]) / 1000)
                    t1_align_end_values.append(float(row[align_end_key]) / 1000)

            # Extraire les valeurs d'alignement pour la phrase entière (sent)
            sent_align_begin = float(row['Sent_AlignBegin']) / 1000
            sent_align_end = float(row['Sent_AlignEnd']) / 1000
            sent_id = row['Sent_ID']

            # Construire le nom du fichier texte correspondant
            if file_name.startswith('ABJ'):
                txt_file_name = '_'.join(file_name.split('_')[:3])
            else:
                txt_file_name = '_'.join(file_name.split('_')[:2])

            text_file_path = glob.glob(f"{text_files_directory}/{txt_file_name}.txt")[0]

            # Ouvrir le fichier texte correspondant
            with open(text_file_path, 'r') as file:
                file_content = file.readlines()

            # Extraire les valeurs correspondantes pour chaque syllabe T1
            for align_begin, align_end in zip(t1_align_begin_values, t1_align_end_values):
                if align_begin > 0:
                    values, nomb = extract_values_from_text_file(file_content, align_begin, align_end)
                    data.append({
                        'align_begin': align_begin,
                        'align_end': align_end,
                        'values': values,
                        'nombres_correspondants': nomb
                    })

            # Extraire les valeurs correspondantes pour la phrase entière (sent)
            sent_form_values, sent_form_nomb = extract_values_from_text_file(
                file_content, sent_align_begin, sent_align_end
            )

            output_file_path = f"{output_directory}/{sent_id}_{id_T1}.txt"
            # Enregistrer les résultats dans un fichier texte
            save_results_to_text_file(output_file_path, sent_id, form, data, sent_align_begin,
                                      sent_align_end, sent_form_values)


def save_results_to_text_file(file_path, sent_id, form, data, sent_align_begin, sent_align_end,
                              sent_form_values):
    # Écrire les résultats dans un fichier texte
    with open(file_path, 'w') as file:
        file.write(f"Sent_ID: {sent_id}\n")

        for i, data in enumerate(data):
            align_begin = data['align_begin']
            align_end = data['align_end']
            values = data['values']
            nomb = data['nombres_correspondants']

            if len(values) > 0:
                file.write(f"Token: {form}\n")
                file.write(f"t1_syl{i + 1}: {align_begin}-{align_end}\n")
                file.write(f"t1_syl{i + 1}_form_values = {values}\n")
                file.write(f"t1_syl{i + 1}_form_nomb = {nomb}\n")
                moyenne_syl = sum(values) / len(values)
                file.write(f"moyenne_syl{i + 1} = {moyenne_syl}\n")
            else:
                file.write(f"moyenne_syl{i + 1} = 0\n")

        file.write(f"Sent_Align: {sent_align_begin}-{sent_align_end}\n")
        file.write(f"value = {sent_form_values}\n")

        if sent_form_values:
            moyenne_sent = sum(sent_form_values) / len(sent_form_values)
            file.write(f"moyenne_sent = {moyenne_sent}\n")
        else:
            file.write("moyenne_sent = 0\n")


tsv_file_path = 'TSV/align_begin_align_end_syl_29_01.tsv'
text_files_directory = 'pitchtier_18janv/txt/'
output_directory = 'pitchtier_18janv/txt_syll/'

# Appeler la fonction principale pour extraire les valeurs et enregistrer les résultats
extract_points_values_from_tsv(tsv_file_path, text_files_directory, output_directory)
