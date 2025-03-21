import streamlit as st

import time

import numpy as np

import pandas as pd

from code_01 import genre_based_recommendation, movie_name_to_movie_id,recommendation_pipeline_01,movie_ids_to_movie_names, get_main_actor, get_data_of_movie_release,save_movie_recommendations_as_csv


from code_01 import add_rating_of_movie_to_user_rec_history

from code_01 import decode_user_ratings_01

import pickle
import ast


# from code.source_code.code_01 import genre_based_recommendation


st.title('Movie Recommendation Engine - Version 0002')


st.write("Please select recommendation engine you want to use")


if 'clicked_on_content_based' not in st.session_state:
    st.session_state.clicked_on_content_based = False
# if 'clicked_rec_engine' not in st.session_state:
#     st.session_state.clicked_rec_engine = False
if 'clicked_on_peer_based' not in st.session_state:
    st.session_state.clicked_on_peer_based = False

def click_on_content_based():
    if st.session_state.clicked_on_content_based:
        st.session_state.clicked_on_content_based = False
    else:
        st.session_state.clicked_on_content_based = True

def click_on_peer_based():
    if st.session_state.clicked_on_peer_based:
        st.session_state.clicked_on_peer_based = False
    else:
        st.session_state.clicked_on_peer_based = True

st.button("Content based", on_click=(click_on_content_based))

st.button("Peer based", on_click=(click_on_peer_based))

if st.session_state.clicked_on_content_based:

    st.header('Content based engine')

    st.write('Please enter a movie name. (Note: If the movie name is found the engine will generate movie recommendations based on this movie.)')

    movie_name = st.text_input("Movie name", "Life of Brian")

    st.write("The current movie title is:", movie_name)


    movie_id = movie_name_to_movie_id(movie_name)
    if len(movie_id) == 0:
        st.write("No movie_id can be found for the following movie_name: ", movie_name)
        st.write("Please check spelling and the date at which the movie was released. Movies newer than 2014? are not in the database.")
    else:
        st.write("This is the found movie_id: ", movie_id)


    if 'clicked_basic_information' not in st.session_state:
        st.session_state.clicked_basic_information = False
    # if 'clicked_rec_engine' not in st.session_state:
    #     st.session_state.clicked_rec_engine = False
    if 'clicked_saving_as_csv' not in st.session_state:
        st.session_state.clicked_saving_as_csv = False


    # ## Test
    # if 'clicked' not in st.session_state:
    #     st.session_state.clicked = False

    # def click_button():
    #     if st.session_state.clicked:
    #         st.session_state.clicked = False
    #     else:
    #         st.session_state.clicked = True

    # st.button('Click me', on_click=click_button)

    # if st.session_state.clicked:
    #     # The message and nested widget will remain on the page
    #     st.write('Button clicked!')
    #     st.slider('Select a value')
    # else:
    #     st.write("button is not clicked.")
    # ## Test end


    def click_button_basic_information():
        if st.session_state.clicked_basic_information:
            st.session_state.clicked_basic_information = False
        else:
            st.session_state.clicked_basic_information = True

    st.button("Show basic information about movie", type= "secondary", on_click=click_button_basic_information)

    main_actor = get_main_actor(movie_id)
    movie_release_date = get_data_of_movie_release(movie_id)

    if st.session_state.clicked_basic_information:
        st.subheader("Basic information about movie")

        st.write("Main Actor: ", main_actor)
        st.write("Movie release date: ", movie_release_date)

        # movie_information_dict = {"Movie Title": [movie_name], 
        #                       "Main Actor": [get_main_actor(movie_id)], 
        #                       "Release date": [get_data_of_movie_release(movie_id)]}

        # st.write(pd.DataFrame(data= movie_information_dict).iloc[0].T)

    # st.subheader("Recommended movies are the following:")


    # if st.button("Run", type="primary"):
    #     st.write("Programm is  running.")
    # else:
    #     st.write("No programm is running.")

    def click_button_saving_as_csv():
        if st.session_state.clicked_saving_as_csv:
            st.session_state.clicked_saving_as_csv =False
        else:
            st.session_state.clicked_saving_as_csv = True

    st.button("Save Movie Recommendations", type="secondary", on_click=click_button_saving_as_csv)

    if st.session_state.clicked_saving_as_csv:
        st.write("Saving movie input and movie recommendations as csv activated.")
    else:
        st.write("Saving not activated.")

    # def click_button_rec_engine():
    #     st.session_state.clicked_rec_engine = True

    # st.button("Run Recommendation Engine", type="primary", on_click=click_button_rec_engine)

    # st.button("Reset", type="primary")
    if st.button("Run Recommendation Engine", type="primary"):
        st.write("Recommendation programm was started.")
        genre_rec_movie_ids, actor_rec_movie_ids = recommendation_pipeline_01(movie_id)
        rec_movie_names = movie_ids_to_movie_names(actor_rec_movie_ids)

        rec_movie_names.remove(movie_name)
        # st.write(movie_id)
        # st.write(actor_rec_movie_ids)
        actor_rec_movie_ids.remove(int(movie_id))
        # st.write(actor_rec_movie_ids)

        movie_information_dict = {"Movie Title": [movie_name], 
                            "Main Actor": [get_main_actor(movie_id)], 
                            "Release date": [get_data_of_movie_release(movie_id)]}
        
        movie_information_df = pd.DataFrame(data= movie_information_dict).rename({0: "Movie Input"}).iloc[0]

        # st.write(pd.DataFrame(data= movie_information_dict).iloc[0].T)

        st.write("Based on this movie input", movie_information_df , "the following " + str(len(rec_movie_names)) + " movies are recommended.")

        # st.subheader("The following movies are recommended")

        # st.write("In total " + str(len(rec_movie_names)) + " movies are recommended")

        release_dates_of_rec_movies = []
        for i in actor_rec_movie_ids:
            release_dates_of_rec_movies.append(get_data_of_movie_release(i)) 

        rec_movies_information_dict = {"Movie Title": rec_movie_names, "Release date": release_dates_of_rec_movies}


        rec_movie_names_df = pd.DataFrame(data= rec_movies_information_dict)
        st.write(rec_movie_names_df)
            



        st.write("Recommendation engine stopped.")

        if st.session_state.clicked_saving_as_csv:
            st.write("Saving movies input and recommended movies...")
            save_movie_recommendations_as_csv(rec_movie_names_df, movie_information_df)
            st.write("Saving movies input and recommended movies finished.")
        else:
            st.write("Recommendations are not saved.")


    else:
        st.write("No programm is running.")




    # if st.button("Aloha", type="primary"):
    #     st.write("Ciao")

    # st.button("Reset", type="primary")
    # if st.button("Say hello"):
    #     st.write("Why hello there")
    # else:
    #     st.write("Goodbye")

    # if st.button("Aloha", type="primary"):
    #     st.write("Ciao")

    # genre_rec_movie_ids, actor_rec_movie_ids = recommendation_pipeline_01(movie_id)

    # actor
if 'clicked_on_want_to_add_ratings' not in st.session_state:
    st.session_state.clicked_on_want_to_add_ratings = False

def click_on_add_ratings():
    if st.session_state.clicked_on_want_to_add_ratings:
        st.session_state.clicked_on_want_to_add_ratings = False
    else:
        st.session_state.clicked_on_want_to_add_ratings = True

# if 'clicked_run_peer_based_engine' not in st.session_state:
#     st.session_state.clicked_run_peer_based_engine = False

# def click_on_run_peer_based_engine():
#     if st.session_state.clicked_run_peer_based_engine:
#         st.session_state.clicked_run_peer_based_engine = False
#     else:
#         st.session_state.clicked_run_peer_based_engine = True

if st.session_state.clicked_on_peer_based:
        st.header('Peer based engine')

        st.button("I want to add ratings", on_click=click_on_add_ratings)


        if st.button("initialize and save dummy user recommendation history"):
            user_rec_history = pd.DataFrame(columns=["movieId", "rating"])
            user_rec_history.to_csv("../../data/peer_based_01_datastorage/dummy_user_rec_history.csv")


        # if st.button("save user rec history"):

        if st.session_state.clicked_on_want_to_add_ratings:



            st.write('Please enter a movie name you want to rate. (Note: If the movie name is found you can rate this movie.)')

            seach_movie_name = st.text_input("Enter movie name you want to rate", "Life of Brian")



            movie_id_peer_based = movie_name_to_movie_id(seach_movie_name)
            if len(movie_id_peer_based) == 0:
                st.write("No movie_id can be found for the following movie_name: ", seach_movie_name)
                st.write("Please check spelling and the date at which the movie was released. Movies newer than 2014? are not in the database.")
            else:
                st.write("This is the found movie_id: ", movie_id_peer_based)
                # user_rating = float(input("Please rate this movie"))
                # seach_movie_name = st.text_input("Enter movie name you want to rate", 5)

                sentiment_mapping = ["one", "two", "three", "four", "five"]
                selected = st.feedback("stars")
                if selected is not None:
                    st.markdown(f"You selected {sentiment_mapping[selected]} star(s).")

                user_rating = selected + 1



        if st.button("Add rating to rec history and save it"):

            user_rec_history = pd.read_csv("../../data/peer_based_01_datastorage/dummy_user_rec_history.csv", index_col=0)

            user_rec_history = add_rating_of_movie_to_user_rec_history(user_rec_history, movie_id_peer_based, user_rating)

            user_rec_history.to_csv("../../data/peer_based_01_datastorage/dummy_user_rec_history.csv")

        # if st.button("Save rating history"):

            

                # if st.button("Show current ratings of movies"):
                # # user_rec_history = pd.read_csv("../../data/peer_based_01_datastorage/dummy_user_rec_history.csv", index_col=0)
                #     st.write(user_rec_history)
                    # st.write("Show current ratings of movies in database: ", user_rec_history)

        user_rec_history = pd.read_csv("../../data/peer_based_01_datastorage/dummy_user_rec_history.csv", index_col=0)

        st.write("Show current ratings of movies in database: ", user_rec_history)


        

        if st.button("Run peer based recommendation engine"):

            sum, sum_scaled = decode_user_ratings_01(user_rec_history)




            # load
            with open('model_kmeans_20_clusters_01.pkl', 'rb') as f:
                clf2 = pickle.load(f)

            
            kmeans_results_20_02 = clf2.predict(sum_scaled.T)

            st.write("Based on your rating input, you belong to the cluster number: " + str(int(kmeans_results_20_02[0])))


            cluster_data = pd.read_csv("../../data/peer_based_01_datastorage/sample_20_cluster_with_movie_ids_and_names_01.csv",index_col=0)

            get_cluster_row = cluster_data.loc[cluster_data["label"] == int(kmeans_results_20_02)]

            s_02 = get_cluster_row["movie_names"].values[0]


            lst_02 = ast.literal_eval(s_02)



            st.write("Number of movies found: ", len(lst_02))

            if len(lst_02) > 10:
                # st.write(lst_02[0:10])
                
                st.write("Ten of the recommended movies list:")
                st.write(pd.DataFrame(lst_02[0:10], columns=["Movie Names"]))
            else:
                # st.write(lst_02)

                st.write(pd.DataFrame(lst_02, columns=["Movie Names"]))

# progress_bar = st.sidebar.progress(0)
# status_text = st.sidebar.empty()
# last_rows = np.random.randn(1, 1)
# chart = st.line_chart(last_rows)

# for i in range(1, 101):
#     new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
#     status_text.text(f"{i}% complete")
#     chart.add_rows(new_rows)
#     progress_bar.progress(i)
#     last_rows = new_rows
#     time.sleep(0.05)

# progress_bar.empty()

# # Streamlit widgets automatically run the script from top to bottom. Since
# # this button is not connected to any other logic, it just causes a plain
# # rerun.
# st.button("Rerun")



# Notizen:

# 
# Das Design kann ich mir noch besser überlegen...
# 