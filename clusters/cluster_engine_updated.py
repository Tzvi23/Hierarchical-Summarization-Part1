#!/usr/bin/env python

def run_kmeans(cluster_path, output_plots, custom_files=None, output_report_file=None):
    import numpy as np  # linear algebra
    import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import normalize
    from sklearn.metrics import pairwise_distances
    from sklearn.metrics import davies_bouldin_score
    from sklearn.metrics import silhouette_score
    from sklearn.metrics.pairwise import paired_euclidean_distances
    from scipy.spatial import distance  # Calculate distance between points
    import os
    import nltk
    import string

    import matplotlib.pyplot as plt

    results_dict = {}

    # Check if output dir exists and create if need
    if not os.path.exists(output_plots):
        os.mkdir(output_plots)

    report_file = None  # declaration
    if output_report_file is not None:
        report_file = open(output_report_file, 'w')
        report_file.write(str(custom_files) + '\n')  # write the file names used
        report_file.write('Number of files: ' + str(len(custom_files)) + '\n')

    # ### Load the .csv file with all the data to be clustered
    print('[!!] Load data ...')
    df = pd.read_csv(cluster_path)
    print(df.head())

    if custom_files is not None:
        sort_list = [fileName[:-4] for fileName in custom_files]
        df = df[df.file_id.isin(sort_list)]

    # #### Take just the text column and lower all the text
    data = df['text'].str.lower()

    print(f'Number of empty rows: {data.isna().sum()}')  # Shows how many empty rows exists
    data = data.dropna()  # Drops the row that are empty
    print(f'Number of empty rows after .dropna: {data.isna().sum()}')  # Shows how many empty rows exists after dropna

    print('[!!] Activating TFidfVectorizer ...')
    tf_idf_vectorizor = TfidfVectorizer(stop_words='english', max_features=20000)
    tf_idf = tf_idf_vectorizor.fit_transform(data)
    tf_idf_norm = normalize(tf_idf)
    tf_idf_array = tf_idf_norm.toarray()

    # #### Feature names
    print(pd.DataFrame(tf_idf_array, columns=tf_idf_vectorizor.get_feature_names()).head())

    # ## PCA
    print('[!!] Building PCA ...')
    sklearn_pca = PCA(n_components=2)
    Y_sklearn = sklearn_pca.fit_transform(tf_idf_array)

    plt.scatter(Y_sklearn[:, 0], Y_sklearn[:, 1], s=50, cmap='viridis')
    plt.savefig(os.path.join(output_plots, 'PCA.png'))
    plt.clf()
    # ## K- Means
    print('[!!] Creating Kmeans object with 3 clusters ...')
    estimater = KMeans(n_clusters=3)
    estimater.fit(Y_sklearn)
    predicted_values = estimater.predict(Y_sklearn)

    plt.scatter(Y_sklearn[:, 0], Y_sklearn[:, 1], c=predicted_values, s=50, cmap='viridis')
    centers = estimater.cluster_centers_
    plt.scatter(centers[:, 0], centers[:, 1], c='black', s=300, alpha=0.6)
    plt.savefig(os.path.join(output_plots, 'clusters.png'))
    plt.clf()

    # #### davies_bouldin_score
    print("davies_bouldin_score: ")
    db_score = davies_bouldin_score(Y_sklearn, predicted_values)
    results_dict['davies_bouldin_score'] = db_score
    print(db_score)
    if report_file is not None:
        report_file.write('[!] Davies Bouldin: \n')
        report_file.write(str(db_score) + '\n')

    # #### Silhouette score
    print('Silhouette score: ')
    sil_score = silhouette_score(Y_sklearn, predicted_values)
    results_dict['silhouette_score'] = sil_score
    print(sil_score)
    if report_file is not None:
        report_file.write('[!] Silhouette score: ' + str(sil_score) + '\n')

    # #### Cluster centers
    print('Cluster centers:')
    print(estimater.cluster_centers_)
    if report_file is not None:
        report_file.write('[!] Cluster centers: \n')
        report_file.write(str(estimater.cluster_centers_) + '\n')

    # ## Calculate distance between centroids
    centroid_distance = distance.cdist(estimater.cluster_centers_, estimater.cluster_centers_, 'euclidean')
    print('Distance between centroids:')
    print(centroid_distance)
    if report_file is not None:
        report_file.write('[!] Distance between centroids: \n')
        report_file.write(str(centroid_distance) + '\n')

    # ## M1 - Average distance between centroids
    M1 = np.mean(np.unique(centroid_distance[np.nonzero(centroid_distance)]))
    print(f'M1 - Average distance between cnetroids: {M1}')
    results_dict['M1'] = M1
    min_distance_cluster = np.min(
        centroid_distance[np.nonzero(centroid_distance)])  # Find minimum value in centroid distance
    print(f'Minimum distance between centroids: {min_distance_cluster}')

    # #### Dunn Index
    min_distance_cluster = np.min(
        centroid_distance[np.nonzero(centroid_distance)])  # Find minimum value in centroid distance
    print(f'Minimum distance between centroids: {min_distance_cluster}')
    if report_file is not None:
        report_file.write('[!] Minimum distance between centroids: ' + str(min_distance_cluster) + '\n')

    results = predicted_values.reshape(predicted_values.shape[0], 1)
    results = np.concatenate((Y_sklearn, results), axis=1)

    # Cluster 0 max distance
    cluster0 = results[np.where(results[:, 2] == 0)][:, [0, 1]]
    cluster0_X = cluster0[:, 0].reshape(cluster0[:, 0].shape[0], 1)
    cluster0_Y = cluster0[:, 1].reshape(cluster0[:, 1].shape[0], 1)
    cluster0_distance = paired_euclidean_distances(cluster0_X, cluster0_Y)
    cluster0_max_distance = np.max(cluster0_distance)
    print(f'Cluster 0 max distance: {cluster0_max_distance}')

    # Cluster 1 max distance
    cluster1 = results[np.where(results[:, 2] == 1)][:, [0, 1]]
    cluster1_X = cluster1[:, 0].reshape(cluster1[:, 0].shape[0], 1)
    cluster1_Y = cluster1[:, 1].reshape(cluster1[:, 1].shape[0], 1)
    cluster1_distance = paired_euclidean_distances(cluster1_X, cluster1_Y)
    cluster1_max_distance = np.max(cluster1_distance)
    print(f'Cluster 1 max distance: {cluster1_max_distance}')

    # Cluster 2 max distance
    cluster2 = results[np.where(results[:, 2] == 2)][:, [0, 1]]
    cluster2_X = cluster2[:, 0].reshape(cluster2[:, 0].shape[0], 1)
    cluster2_Y = cluster2[:, 1].reshape(cluster2[:, 1].shape[0], 1)
    cluster2_distance = paired_euclidean_distances(cluster2_X, cluster2_Y)
    cluster2_max_distance = np.max(cluster2_distance)
    print(f'Cluster 1 max distance: {cluster2_max_distance}')

    # Dunn score
    max_distance = max(cluster0_max_distance, cluster1_max_distance, cluster2_max_distance)
    print(f'Max distance in cluster: {max_distance}')
    print(f'Min distance between centroids: {min_distance_cluster}')
    dunn_index_value = min_distance_cluster / max_distance
    print(f'Dunn index value: {dunn_index_value}')
    results_dict['dunn_index'] = dunn_index_value

    if report_file is not None:
        report_file.write('[!] Dunn score: ' + str(dunn_index_value) + '\n')

    # ## Avg distance to centroid
    # ### Transform the predicted values to values as distance to center of the centroid
    res = estimater.transform(Y_sklearn)

    # ## M2 Intra cluster distance for each cluster:
    # ### Average distance to centroid
    # Add cluster classification to the array for filtering
    pred_vals = predicted_values.reshape(predicted_values.shape[0], 1)
    res_cluster = np.concatenate((res, pred_vals), axis=1)
    print(res_cluster)
    # Extract distance to centroid for each cluster
    dist_cluster0 = res_cluster[np.where(res_cluster[:, 3] == 0)][:, 0]
    dist_cluster1 = res_cluster[np.where(res_cluster[:, 3] == 1)][:, 1]
    dist_cluster2 = res_cluster[np.where(res_cluster[:, 3] == 2)][:, 2]
    # Calc average distance to centroid for each cluster
    avg_dist_cluster0 = np.mean(dist_cluster0)
    avg_dist_cluster1 = np.mean(dist_cluster1)
    avg_dist_cluster2 = np.mean(dist_cluster2)
    # Total average of distance to centroid
    M2_total_avg_dist = np.mean([(avg_dist_cluster0, avg_dist_cluster1, avg_dist_cluster2)])
    # Print values
    print(f'Cluster 0 Avg distance to centroid: {avg_dist_cluster0}')
    print(f'Cluster 1 Avg distance to centroid: {avg_dist_cluster1}')
    print(f'Cluster 1 Avg distance to centroid: {avg_dist_cluster2}')
    print(f'[M2] Total average distance to centroid: {M2_total_avg_dist}')
    results_dict['M2'] = M2_total_avg_dist

    # ## M3 - Maximum Radius
    cluster0_max_radius = np.max(dist_cluster0)
    cluster1_max_radius = np.max(dist_cluster1)
    cluster2_max_radius = np.max(dist_cluster2)
    M3_maximum_radius = np.max([(cluster0_max_radius, cluster1_max_radius, cluster2_max_radius)])
    print(f'Cluster 0 Max Radius: {cluster0_max_radius}')
    print(f'Cluster 1 Max Radius: {cluster1_max_radius}')
    print(f'Cluster 2 Max Radius: {cluster2_max_radius}')
    print(f'[M3] Maximum Radius: {M3_maximum_radius}')
    results_dict['M3'] = M3_maximum_radius

    # ## M4 - Average Radius
    M4_avg_radius = np.mean([(cluster0_max_radius, cluster1_max_radius, cluster2_max_radius)])
    print(f'[M4] Average Radius: {M4_avg_radius}')
    results_dict['M4'] = M4_avg_radius

    # Each column is values of distances to each centroid
    print(f'Shape: {res.shape}')

    # Calculate the avg distance in each row of the np array
    avg_distance = np.mean(res, axis=0)  # axis=1 rows ; axis=0 columns
    print('Avg distance to centroid:')
    print(f'Cluster 1: {avg_distance[0]}')
    print(f'Cluster 2: {avg_distance[1]}')
    print(f'Cluster 3: {avg_distance[2]}')

    if report_file is not None:
        report_file.write('[!] Avg distance to centroid: \n')
        report_file.write(f'Cluster 1: {avg_distance[0]}' + '\n')
        report_file.write(f'Cluster 2: {avg_distance[1]}' + '\n')
        report_file.write(f'Cluster 3: {avg_distance[2]}' + '\n')
    # ## Purity

    # $Purity = \frac 1 N \sum_{i=1}^k max_j | c_i \cap t_j |$
    # - N - Number of nodes
    # - K - Number of clusters (in our case K = 3)
    # - C - Ground truth clusters
    # - t - Results classification

    # ### Creating ground truth

    # backup variables
    t_predicted_values = predicted_values
    ground_truth = Y_sklearn

    # reshaping for concat
    t = t_predicted_values.reshape(ground_truth.shape[0], 1)

    print(f'Predicted values shape: {t.shape}')

    print(f'Y_sklearn shape: {ground_truth.shape}')

    # ### Concat the arrays
    # #### Now we have ground truth classification of the data : (axis, axis, cluster)

    ground_truth = np.concatenate((ground_truth, t), axis=1)

    print(pd.DataFrame(ground_truth, columns=['axis1', 'axis2', 'cluster']).head())

    x, y = np.unique(ground_truth[:, 2], return_counts=True)

    x = [int(v) for v in x.tolist()]
    total = np.sum(y)
    y = [int(v) for v in y.tolist()]
    x_y = dict(zip(x, y))
    print(f'Total: {total}')

    plt.bar(x, y)
    plt.savefig(os.path.join(output_plots, 'purity.png'))
    plt.clf()
    print(x_y)
    if report_file is not None:
        report_file.write('[!] Purity \n')
        report_file.write('[!] Ground truth: \n')
        report_file.write(str(x_y) + '\n')

    def create_confusion_matrix(truth):
        con_matrix = {0: list(), 1: list(), 2: list()}
        values = list(map(int, truth[:, 2]))
        for index in range(len(values)):
            con_matrix[values[index]].append(index)
        return con_matrix

    return create_confusion_matrix(ground_truth), results_dict
