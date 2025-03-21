# import necessary libraries

import json
import numpy as np

import pandas as pd

from scipy.spatial.distance import cosine


from os import listdir
from os.path import isfile, join

from tqdm import tqdm

from datetime import datetime

print("load data")


FOLDER_PATH = "../../data/archive/"

FOLDER_PATH_SAVING = "../../user_experience_01/"

ONLYFILES = [f for f in listdir(FOLDER_PATH) if isfile(join(FOLDER_PATH, f))]


MOVIES_METADATA_DF = pd.read_csv(FOLDER_PATH+ONLYFILES[4])

RATINGS_DF = pd.read_csv(FOLDER_PATH+ONLYFILES[5], header=0)


DECODED_MOVIES_DF = pd.read_csv("../../data/transformed_data/decoded_movies.csv", header=0, index_col=0)


def convert_str_to_python_objects(str_01):
    str_02 = str_01.replace("'", '"')
    str_03 = json.loads(str_02)
    return str_03


def decode_movies(movies_md):
    for index in range(len(movies_md)):
        # print(index)
        # print(movies_md.iloc[index])
        DECODED_MOVIES_DF.loc[index, "movie_id"] = movies_md.iloc[index]["id"]
        DECODED_MOVIES_DF.loc[index, "original_title"] = movies_md.iloc[index]["original_title"]
        movie_genres = convert_str_to_python_objects(movies_md.iloc[index]["genres"])
        # existing_genre = 
        for genre_name in genre_names_list:
            DECODED_MOVIES_DF.loc[index, genre_name] = 0
        for movie_genre in movie_genres:
            DECODED_MOVIES_DF.loc[index, movie_genre["name"]] = 1
    return DECODED_MOVIES_DF



def find_all_cast_names_in_movie(cast_string):

    names = []
    beginning = 0

    if True: 
        while "'name': '" in cast_string[beginning:]:
            beginning = cast_string[beginning:].find("'name':") + len("'name': '") + beginning

            ending = cast_string[beginning:].find("'")
        # name = cast_string[beginning:beginning+ending]

        
            names.append(cast_string[beginning:beginning+ending])
        # beginning = beginning+1

    else:
        beginning = cast_string[beginning:].find("'name':") + len("'name': '") + beginning
        ending = cast_string[beginning:].find("'")
        names.append(cast_string[beginning:beginning+ending])

    return names



# convert movie ids to movie names and vice versa
def movie_ids_to_movie_names(movie_id_list):
    movie_name_list = []
    print("log: loading movie metadata...")
    # load movie metadate to get names of movies
    # movies_metadata = pd.read_csv(FOLDER_PATH+ONLYFILES[4])


    for movie_id in movie_id_list:
        # print(i)
        # movie_name_list.append(movie_id_to_movie_name(movie_id))
        movie_name_list.append(list(MOVIES_METADATA_DF.loc[MOVIES_METADATA_DF["id"] == str(movie_id)]["original_title"])[0])
        # print(movie_name_list)

    return movie_name_list

def movie_id_to_movie_name(movie_id):
    print("log: loading movie metadata...")
    # load movie metadate to get names of movies
    movies_metadata = pd.read_csv(FOLDER_PATH+ONLYFILES[4])

    movie_name = list(movies_metadata.loc[movies_metadata["id"] == str(movie_id)]["original_title"])[0]

    return movie_name

def movie_name_to_movie_id(movie_name):
    print("log: loading movie metadata...")
    # load movie metadate to get names of movies
    movies_metadata = pd.read_csv(FOLDER_PATH+ONLYFILES[4])


    movie_id = movies_metadata.loc[movies_metadata["original_title"] ==  movie_name]["id"]

    if len(movie_id) == 0:
        print("No movie_id can be found for the following movie_name: " + str(movie_name))
        print("Please check spelling and the date at which the movie was released.")
    else:
        movie_id = list(movie_id)[0]
        print("The movie_id for the requested movie_name is: " + str(movie_id))
    return movie_id


def filter_movies_after_actors(movie_id, genre_filtered_movies_ids):
    actor_filtered_movie_ids = []
    

    print("log: loading credits data...")
    credits_df = pd.read_csv(FOLDER_PATH+ONLYFILES[0])
    
    actor_01 = find_all_cast_names_in_movie(list(credits_df.loc[credits_df["id"] == int(movie_id)]["cast"])[0])[0]
    print("log: check for actors in movies")
    for i in tqdm(genre_filtered_movies_ids):
        cast_string_01 = list(credits_df.loc[credits_df["id"] == int(i)]["cast"])[0]
        # print(cast_string_01)
        actor_names = find_all_cast_names_in_movie(cast_string_01)

        if actor_01 in actor_names:
            actor_filtered_movie_ids.append(i)

    # actor_filtered_movie_names = movie_ids_to_movie_names(actor_filtered_movie_ids)

    return actor_filtered_movie_ids#, actor_filtered_movie_names




def genre_based_recommendation(movie_id):

    print("log: loading movie metadata...")
    # load movie metadate to get names of movies
    movies_metadata = pd.read_csv(FOLDER_PATH+ONLYFILES[4])

    print("log: loading decoded movie genre data...")
    # loaded decoded data for genre similarity check
    
    
    recommended_movies_ids = []
    recommended_movies_names = []


    # get right format for the movie
    
    movie_01 = list(DECODED_MOVIES_DF.loc[DECODED_MOVIES_DF["movie_id"] == int(movie_id)].iloc[0,2:])


    final_list = find_movie_with_highest_sim(movie_01, DECODED_MOVIES_DF)

    print("log: finding the indices with maximum values")
    indices = [i for i, x in tqdm(enumerate(final_list)) if x == max(final_list)]

    print("log: generating movie ids list with highest similarity...")
    for i in indices:
        recommended_movies_ids.append(DECODED_MOVIES_DF.iloc[i]["movie_id"])

    # print("log: generating movie names list with highest similarity...")
    # for i in recommended_movies_ids:
    #     recommended_movies_names.append(list(movies_metadata.loc[movies_metadata["id"] == str(i)]["original_title"])[0])

    print("log: task finished.")
    return recommended_movies_ids


def find_movie_with_highest_sim(one_movie, all_other_movies):
    print("log: computing cosine similarity between movies...")
    dummy_list = []
    for i in tqdm(range(len(all_other_movies))):
        second_movie = list(DECODED_MOVIES_DF.iloc[i,2:])
        cos_sim = 1 - cosine(one_movie, second_movie)
        dummy_list.append(round(cos_sim,4))
    return dummy_list




# recommendation engine pipeline
def recommendation_pipeline_01(movie_id):
    genre_rec_movie_ids = genre_based_recommendation(movie_id)

    actor_rec_movie_ids = filter_movies_after_actors(movie_id,genre_rec_movie_ids)
    
    return genre_rec_movie_ids, actor_rec_movie_ids


def get_main_actor(movie_id):

    print("log: loading credits data...")
    credits_df = pd.read_csv(FOLDER_PATH+ONLYFILES[0])
    
    main_actor = find_all_cast_names_in_movie(list(credits_df.loc[credits_df["id"] == int(movie_id)]["cast"])[0])[0]
    return main_actor

def get_data_of_movie_release(movie_id):

    print("log: loading movie metadata...")
    # load movie metadate to get names of movies
    movies_metadata = pd.read_csv(FOLDER_PATH+ONLYFILES[4])

    release_date = list(movies_metadata.loc[movies_metadata["id"] == str(movie_id)]["release_date"])[0]
    return release_date


def save_movie_recommendations_as_csv(rec_movie_names_df, movie_information_df):
    print("saving movie recommendations and movie input ...")
    current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    movie_information_df.to_csv(FOLDER_PATH_SAVING +"movie_input_"+ current_datetime +".csv")
    rec_movie_names_df.to_csv(FOLDER_PATH_SAVING +"recommend_movies_"+ current_datetime +".csv")
    print("saving movie recommendations and movie input finished.")


def generate_movie_ids_cleaned(movies_metadata):
    movie_ids_cleaned = []

    for i in movies_metadata["id"]:
        # print(i)
        if i == "1997-08-20":
            pass
            # print("ERSETZEN!!!")
        elif i == "2012-09-29":
            pass
            # print("ERSETZEN!!!")
        elif i == "2014-01-01":
            pass
            # print("ERSETZEN!!!")
        else:
            movie_ids_cleaned.append(int(i))

    return movie_ids_cleaned

def filter_ratings(ratings_input_df, movie_ids_cleaned_input):
    # filtered_rating_df = pd.DataFrame(columns= ratings_input_df.columns)
    first_time = True
    for index in tqdm(range(len(ratings_input_df))): # in tqdm(range(10)): 
        # print(index)
        rating_entry = ratings_input_df.iloc[index]
        # print(rating_entry)
        if rating_entry["movieId"] in movie_ids_cleaned_input:
            if first_time:
                filtered_rating_df = pd.DataFrame(rating_entry)
                # print(filtered_rating_df)
                first_time = False
     
            else:
                filtered_rating_df = pd.concat([filtered_rating_df, pd.DataFrame(rating_entry)],axis= 1)
            # print(filtered_rating_df)
        # print(type(rating_entry))
            # print(rating_entry)
            # print(filtered_rating_df)

    if first_time:
        return "empty!"
    else:
        return filtered_rating_df.T



def decode_user_ratings_01(filtered_rating_df_input):
    """_ratings_to_one_weighted_genre_vector_per_user"""
    first_entry = True
    for index in tqdm(range(len(filtered_rating_df_input))):
        rating_entry = filtered_rating_df_input.iloc[index]
    
        specific_movie_entry = DECODED_MOVIES_DF.loc[DECODED_MOVIES_DF["movie_id"] == int(rating_entry["movieId"])]

        # if len(specific_movie_entry) == 0:
        #     print(specific_movie_entry)
        #     print(int(rating_entry["movieId"]))

        #     specific_movie_entry = DECODED_MOVIES_DF.loc[DECODED_MOVIES_DF["movie_id"] == str(rating_entry["movieId"])]

        if len(specific_movie_entry) != 0:
            if first_entry:

                sum = np.array(specific_movie_entry.iloc[0,2:] * rating_entry["rating"])
                first_entry = False
                
            else:
                # print(specific_movie_entry.iloc[0,2:])
                sum = np.array(specific_movie_entry.iloc[0,2:] * rating_entry["rating"]) + sum
        
    if not first_entry:
        from sklearn.preprocessing import MinMaxScaler

        minmaxscaler = MinMaxScaler()
        # print(sum)
        sum_scaled = minmaxscaler.fit_transform(pd.DataFrame(sum))

        # round?
        sum_scaled = np.round(sum_scaled,4)
    
        return sum, sum_scaled

    else: 
        return "empty", "empty"


def generate_rec_from_computed_genre_vector(artificial_genre_vector_scaled):
    recommended_movies_ids = []
    final_list = find_movie_with_highest_sim(list(pd.DataFrame(artificial_genre_vector_scaled)[0]), DECODED_MOVIES_DF)
    # get the two highest values
    max1 = max2 = float('-inf')
    for n in final_list:
  
        # If the current number is greater 
        # than largest found so far
        if n > max1:
        
            # Update second largest to the previous largest
            max2 = max1  
            
            # Update largest to the current number
            max1 = n     
            
        # If current number is less than largest
        # but greater than second largest
        elif n > max2 and n != max1:
        
            # Update second largest to current number
            max2 = n  
    # print(max1)
    # print(max2)
    print("log: finding the indices with maximum values and second highest value")
    indices = [i for i, x in tqdm(enumerate(final_list)) if x == max2 or x == max(final_list)]


    print("log: generating movie ids list with highest similarity...")
    for i in tqdm(indices):
        recommended_movies_ids.append(DECODED_MOVIES_DF.iloc[i]["movie_id"])

    print("log: task finished.")

    return recommended_movies_ids



def generate_user_specific_genre_vector(user_id):
    ratings_of_one_user = RATINGS_DF.loc[RATINGS_DF["userId"] == user_id]
    cleaned_movies = generate_movie_ids_cleaned(MOVIES_METADATA_DF)

    filtered_ratings_user = filter_ratings(ratings_of_one_user, cleaned_movies)

    if type(filtered_ratings_user) != str:

        
        sum_user, sum_user_scaled = decode_user_ratings_01(filtered_ratings_user)

        if type(sum_user) == str:
            return "ignore!, since filtered recommendation are empty"
        
        else:
            return sum_user_scaled

    else:
        return "ignore!, since filtered recommendation are empty"

def pipeline_02(user_id):

    sum_user_scaled = generate_user_specific_genre_vector(user_id)
    movie_ids_for_user_genre_vector = generate_rec_from_computed_genre_vector(sum_user_scaled)

    return movie_ids_for_user_genre_vector


def log_progress(message):
    ''' This function logs the mentioned message at a given stage of the 
    code execution to a log file. Function returns nothing.'''

    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now() # get current timestamp 
    timestamp = now.strftime(timestamp_format) 
    with open("./log_datei.txt","a") as f: 
        f.write(timestamp + ' : ' + message + '\n')    


def decode_all_user_ratings():
    all_user_ids = RATINGS_DF.userId.value_counts().index[0:1000]
    first_time = True
    print("go through each user")
    number_of_all_users = len(all_user_ids)
    print("Total number of users:", number_of_all_users)
    for index, user_id_01 in enumerate(all_user_ids):
        print("user_id:", user_id_01)
        print("index:", index)
        sum_user_scaled = generate_user_specific_genre_vector(user_id_01)
        if type(sum_user_scaled) != str:
            user_vector = [user_id_01] + sum_user_scaled.T.tolist()[0]
            column_names = ["user_id"]+list(DECODED_MOVIES_DF.columns[2:])
            user_genre_vectors_dict = {}

            if first_time:
                for i in range(len(user_vector)):
                    user_genre_vectors_dict[column_names[i]] = [user_vector[i]]
                    user_genre_vectors_df = pd.DataFrame(user_genre_vectors_dict)
                first_time = False
            else:
                user_genre_vectors_df.loc[index] = user_vector
        else:
            print("ignore user recommendations!, since filtered recommendations are empty")
        print("##### PRGORESSS #####:", round((index+1)/number_of_all_users, 4))
        log_progress("##### PRGORESSS ####: " + str(round((index+1)/number_of_all_users, 4)))
        if index%25 == 0:
            user_genre_vectors_df.to_csv("../../data/transformed_data/decoded_user_rating_after_5_progress_"+ str(index) + "_von_1000.csv")
    return user_genre_vectors_df


def decode_all_user_clusters_ratings(labeled_user_genre_vectors_df):
    # all_user_ids = ratings.userId.value_counts().index[0:1000]
    print("go through each cluster")
    first_entry = True

    class_labels = labeled_user_genre_vectors_df.label.value_counts().sort_index().index
    print("Total number of clusters:", len(class_labels))

    for index, class_label in enumerate(class_labels):
        print(index)
        print(class_label)
        dummy_df_01 = labeled_user_genre_vectors_df.loc[labeled_user_genre_vectors_df["label"] == class_label]
        dummy_df_02 = pd.DataFrame(dummy_df_01.iloc[:,:-1].sum()).T /dummy_df_01.iloc[:,:-1].sum().max()
        dummy_df_02.loc[:,"label"] = class_label
        # print(dummy_df.columns)
        if first_entry:
            class_genre_vector_df = dummy_df_02
            first_entry = False
        else:
            class_genre_vector_df = pd.concat([class_genre_vector_df, dummy_df_02],axis=0,ignore_index=True)

        # print(class_genre_vector_df.columns)

    
    return dummy_df_02, class_genre_vector_df


def generate_rec_from_computed_genre_vector_02(artificial_genre_vector_scaled):
    recommended_movies_ids = []
    final_list = find_movie_with_highest_sim(artificial_genre_vector_scaled, DECODED_MOVIES_DF)
    # get the two highest values
    max1 = max2 = float('-inf')
    for n in final_list:
  
        # If the current number is greater 
        # than largest found so far
        if n > max1:
        
            # Update second largest to the previous largest
            max2 = max1  
            
            # Update largest to the current number
            max1 = n     
            
        # If current number is less than largest
        # but greater than second largest
        elif n > max2 and n != max1:
        
            # Update second largest to current number
            max2 = n  
    # print(max1)
    # print(max2)
    print("log: finding the indices with maximum values and second highest value")
    indices = [i for i, x in tqdm(enumerate(final_list)) if x == max2 or x == max(final_list)]


    print("log: generating movie ids list with highest similarity...")
    for i in tqdm(indices):
        recommended_movies_ids.append(DECODED_MOVIES_DF.iloc[i]["movie_id"])

    print("log: task finished.")

    return recommended_movies_ids


def add_rating_of_movie_to_user_rec_history(user_rec_history,  movie_id, user_rating):

    user_rec_history.loc[len(user_rec_history)] =  [movie_id] + [user_rating]
 
    return user_rec_history