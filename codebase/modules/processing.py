import numpy as np


# first_filter e.g. T or C
# second_filter e.g. TI, DE
# third_filter e.g. lamb_heavy
def extract_subset(df, first_filter=None, second_filter=None, third_filter=None):
    valid_columns = [col for col in df.columns if len(col.split("#")) == 3]

    lista_sets = []
    if first_filter != None:
        first_set = set(
            [col for col in valid_columns if col.split("#")[0] in first_filter]
        )
        lista_sets.append(first_set)

    if second_filter != None:
        second_set = set(
            [col for col in valid_columns if col.split("#")[1] in second_filter]
        )
        lista_sets.append(second_set)

    if third_filter != None:
        third_filter = set(
            [col for col in valid_columns if col.split("#")[2] in third_filter]
        )
        lista_sets.append(third_filter)

    return list(set.intersection(*lista_sets))


# Ci devono essere almeno len(df) * 0.7 righe non null altrimenti una colonna viene eliminata
def rimuovi_colonne_null(df):
    # Calcolo del numero minimo di valori non mancanti per mantenere la colonna
    min_values = int(0.7 * len(df))

    # Lista delle colonne da rimuovere
    columns_to_drop = [col for col in df.columns if df[col].count() < min_values]

    # Rimozione delle colonne
    df = df.drop(columns=columns_to_drop)

    return df


# Funzione per interpolare valori nulli basati su categorie
def interpola_valori_nulli(df):
    df.interpolate(
        method="linear", limit_area="inside", limit=12, limit_direction="both", axis=0
    )
    df.interpolate(
        method="linear", limit_area="outside", limit=3, limit_direction="both", axis=0
    )

    return df


# Funzione per mantenere colonne con dati nelle ultime x righe
def verifica_dati_recenti(df):
    target_columns = extract_subset(df, first_filter=["T"])

    # Imposta un numero di righe 'n' per selezionare le ultime 50 righe
    n = 50

    # Calcola il numero di valori non mancanti per ogni colonna nelle ultime 'n' righe
    non_missing_counts = df[target_columns].tail(n).notna().sum()

    # Seleziona solo le colonne con meno di 'soglia' valori mancanti nelle ultime 'n' righe
    colonneselezionate = non_missing_counts[non_missing_counts < n * 0.10].index

    # Crea un nuovo DataFrame contenente solo le colonne selezionate
    df = df.drop(columns=colonneselezionate)

    return df


# Funzione per denoising con media mobile
def denoising_media_mobile(df):
    columns = extract_subset(df, first_filter=["C", "T"])
    df[columns] = df[columns].rolling(window=7).mean()
    df = df.dropna(how="all", subset=columns)

    return df


# Funzione per rimuovere outliers con sliding window
def rimuovi_outliers(df, k=3.0):
    for colonna in extract_subset(df, first_filter=["C", "T"]):
        rolling_df = df[colonna].rolling(12)
        Q1 = rolling_df.quantile(0.25)
        Q3 = rolling_df.quantile(0.75)
        IQR = Q3 - Q1

        filtro_outliers = (df[colonna] < (Q1 - k * IQR)) | (
            df[colonna] > (Q3 + k * IQR)
        )

        df.loc[filtro_outliers, colonna] = np.nan
    return df


# Rimuovol le colonne EU e EU+UK
def rimozione_eu_uk(df):
    df = df.drop(columns=extract_subset(df, second_filter=["EU+UK", "EU"]))
    return df
