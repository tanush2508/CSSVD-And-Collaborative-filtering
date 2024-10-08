drive.mount('/content/drive')

import pandas as pd
users_path='/content/drive/MyDrive/STS DATA/users.csv'
user=pd.read_csv(users_path)

import matplotlib.pyplot as plt
import numpy as np

# Drop NaN values from the gender column
gender_values = user['gender'].dropna()

# Create a histogram based on the unique gender values
plt.figure(figsize=(8, 6))
plt.hist(gender_values, bins=np.arange(min(gender_values)-0.5, max(gender_values)+1.5, 1), edgecolor='black', alpha=0.7)
plt.title('Distribution of Gender Values')
plt.xlabel('Gender')
plt.ylabel('Frequency')
plt.xticks(ticks=np.arange(min(gender_values), max(gender_values)+1, 1))
plt.show()

import pandas as pd


df_filtered = user.drop_duplicates()

df_filtered_user=df_filtered.iloc[:-1,:]
# Replace all occurrences of -1 with 0 in the DataFrame
df_filtered_user = df_filtered_user.replace(-1, 0)

df_filtered_user

df_grouped_user = df_filtered_user.groupby('userID').agg({'age': 'mean', 'gender': 'mean'}).reset_index()

# Round down the values
df_grouped_user['age'] = df_grouped_user['age'].apply(lambda x: int(x))
df_grouped_user['gender'] = df_grouped_user['gender'].apply(lambda x: int(x))

np.min(df_grouped_user)

import pandas as pd
import numpy as np

# Extract demographic features (excluding userID)
demographic_df = df_grouped_user.iloc[:, 1:]

# Calculate the Pearson correlation coefficient matrix (x x x)
pcc_matrix = demographic_df.corr(method='pearson')

# Define the penalty threshold
penalty_threshold = demographic_df.shape[1] / 2 + 1

# Apply the improvised PCC formula to adjust similarity scores
improvised_pcc_matrix = pcc_matrix.copy()
for i in range(len(improvised_pcc_matrix)):
    for j in range(len(improvised_pcc_matrix)):
        # Calculate the intersection of users between features i and j
        intersection_users = set(demographic_df[demographic_df.iloc[:, i].notna()].index) & set(demographic_df[demographic_df.iloc[:, j].notna()].index)
        # Calculate the penalty term
        penalty = min(len(intersection_users), penalty_threshold)
        # Apply the improvised PCC formula
        if len(intersection_users) >= penalty_threshold:
            improvised_pcc_matrix.iloc[i, j] = max(0, improvised_pcc_matrix.iloc[i, j])
        else:
            improvised_pcc_matrix.iloc[i, j] = max(0, improvised_pcc_matrix.iloc[i, j]) * penalty / penalty_threshold

# Perform Singular Value Decomposition (SVD) to reduce dimensions to x x k
k = 2  # Specify the desired number of dimensions
U, Sigma, VT = np.linalg.svd(improvised_pcc_matrix)

# Take the top k singular vectors
U_k = U[:, :k]

# Clip negative values to zero
U_k = np.maximum(U_k, 0)

# Display the resulting user demographic matrix
print("User Demographic Matrix (U_k) after clipping negative values:")
print(U_k)

user_features_df = df_grouped_user[['age', 'gender']]
user_feature_matrix = user_features_df @ U_k


user_feature_matrix['userID'] = user['userID']

user_feature_matrix = user_feature_matrix[['userID'] + list(range(k))]
user_feature_matrix = user_feature_matrix.rename(columns={0: 'Feature 1', 1: 'Feature 2'})

np.max(user_feature_matrix)

import pandas as pd
items_path='/content/drive/MyDrive/STS DATA/Item_matrix.csv'
item=pd.read_csv(items_path)

item=item.iloc[:,:7]
item = item.replace(-1, 0)

item

item['creationDate'] = pd.to_datetime(item['creationDate'], errors='coerce')

missing_dates = item['creationDate'].isnull()

date_range = item.loc[~missing_dates, 'creationDate'].max() - item.loc[~missing_dates, 'creationDate'].min()

item['creationDate'] = (item['creationDate'] - item['creationDate'].min()) / date_range

item.loc[missing_dates, 'creationDate'] = -1

item=item.drop(['category3','category'], axis=1)

item

df_filtered_item = item.drop_duplicates()

df_filtered_item

# Replace -1 with NaN
df_filtered_item.replace(-1, np.nan, inplace=True)

# Group by 'ItemID' and calculate the mean for each column
df_grouped_item = df_filtered_item.groupby('itemID').mean()
df_grouped_item.reset_index(inplace=True)
df_grouped_item.fillna(0, inplace=True)

np.min(df_grouped_item)

import pandas as pd
import numpy as np

# Extract item properties (excluding itemID)
item_properties_df = df_grouped_item.iloc[:, 1:]

# Calculate the Pearson correlation coefficient matrix (y * y)
item_pcc_matrix = item_properties_df.corr(method='pearson')

# Define the penalty threshold
penalty_threshold = item_properties_df.shape[1] / 2 + 1

# Apply the improvised PCC formula to adjust similarity scores
improvised_item_pcc_matrix = item_pcc_matrix.copy()
for i in range(len(improvised_item_pcc_matrix)):
    for j in range(len(improvised_item_pcc_matrix)):
        # Calculate the intersection of items between features i and j
        intersection_items = set(item_properties_df[item_properties_df.iloc[:, i].notna()].index) & set(item_properties_df[item_properties_df.iloc[:, j].notna()].index)
        # Calculate the penalty term
        penalty = min(len(intersection_items), penalty_threshold)
        # Apply the improvised PCC formula
        if len(intersection_items) >= penalty_threshold:
            improvised_item_pcc_matrix.iloc[i, j] = max(0, improvised_item_pcc_matrix.iloc[i, j])
        else:
            improvised_item_pcc_matrix.iloc[i, j] = max(0, improvised_item_pcc_matrix.iloc[i, j]) * penalty / penalty_threshold

# Perform Singular Value Decomposition (SVD) to reduce dimensions to y * y
k = 2  # Specify the desired number of dimensions
U_item, Sigma_item, VT_item = np.linalg.svd(improvised_item_pcc_matrix)

# Take the top k singular vectors
U_k_item = U_item[:, :k]

# Clip negative values to zero
U_k_item = np.maximum(U_k_item, 0)

# Display the resulting item property matrix
print("Item Property Matrix (U_k_item) after clipping negative values:")
print(U_k_item)

improvised_item_pcc_matrix

item_properties_df = df_grouped_item[['category2', 'crowdedness','creationDate','knowledgeOfSurroundings']]
# Perform matrix multiplication
item_property_matrix = item_properties_df @ U_k_item

# Concatenate 'itemID' and 'category' columns
item_property_matrix['itemID'] = df_grouped_item['itemID']


# Reorder the columns
item_property_matrix = item_property_matrix[['itemID'] + list(range(k))]

# Rename the feature columns
item_property_matrix = item_property_matrix.rename(columns={0: 'Feature 1', 1: 'Feature 2',2:'Feature 3'})

item_property_matrix

F = np.dot(user_feature_matrix.iloc[:,1:],item_property_matrix.iloc[:,1:].T)

# F = pd.DataFrame(F, columns=item_property_matrix.index, index=user_feature_matrix.index)

np.max(F)

# from google.colab import drive

# drive.mount('/content/drive')

import pandas as pd
ratings_path='/content/drive/MyDrive/STS DATA/ratings.csv'
rating=pd.read_csv(ratings_path)

rating=rating.iloc[:,[0,1,3]]

rating

df_no_duplicates = rating.drop_duplicates(subset=['userID', 'itemID'])

# Group by 'userID' and 'itemID' and calculate the mean of 'rating'
df_grouped_rating = df_no_duplicates.groupby(['userID', 'itemID'])['rating'].mean().reset_index()

# Round down the rating values
df_grouped_rating['rating'] = df_grouped_rating['rating'].apply(lambda x: int(x))

df_grouped_rating

ratings_df = df_grouped_rating.pivot(index='userID', columns='itemID', values='rating')

# Fill missing values with 0
ratings_df.fillna(0, inplace=True)

# Convert itemID columns to integer type
ratings_df.columns = ratings_df.columns.astype(int)

print(np.min(ratings_df))

print(np.max(ratings_df))

import numpy as np
import math

# Define the dimensions of the A_matrix
rows = 1620
columns = 249

# Initialize a A_matrix filled with zeros
A_matrix = np.zeros((rows, columns))

# Assuming you define F and ratings_df somewhere in your code.


ratings_df = ratings_df.to_numpy()

# Define the function to update P_matrix elements
def proximity_of_element(a, b):
    # Example function, you can replace it with your own function
    return 1 - ( 1 / (1 + math.exp( -1 * abs(F[a,b] - ratings_df[a,b]))))

# Calculate the F_median and ratings_median
F_median = np.median(F)
ratings_df_median = np.median(ratings_df)

# Define the function to update Significance_matrix elements
def significance_of_element(a, b):
    # Example function, you can replace it with your own function
    return 1 - ( 1 / (1 + math.exp( -1 * abs(F[a,b] - F_median) * abs(ratings_df[a,b] - ratings_df_median) ) ) )

# Define the function to update Singularity_matrix elements
def singularity_of_element(a, b):
    # Example function, you can replace it with your own function
    return 1 - ( 1 / (1 + math.exp( -1 * ( abs( ((F[a,b] - F[0,b])  + (ratings_df[a,b] - ratings_df[0,b])) / 2 )) ) ) )

# Traverse each element to get it's PSS and construct A_matrix
for a in range(rows):
    for b in range(columns):
        A_matrix[a, b] = proximity_of_element(a,b) * significance_of_element(a,b) * singularity_of_element(a, b)

A_df=A_matrix

A_df

print(np.min(A_df))

A_df.shape

# from google.colab import drive

# drive.mount('/content/drive')

import pandas as pd
context_path='/content/drive/MyDrive/STS DATA/C1.csv'
context=pd.read_csv(context_path)
context=context.iloc[:,:15]
context=context.replace(-1, 0)



context

import pandas as pd
import numpy as np


def calculate_similarity(obj_a, obj_b, omega):
    if obj_a == obj_b and omega == 1:
        return 1
    else:
        return 0

num_contexts = len(context.columns) - 1
contextual_similarity_matrix = np.zeros((num_contexts, num_contexts))


for i, feature_a in enumerate(context.columns[1:]):
    for j, feature_b in enumerate(context.columns[1:]):
        omega = 1  # Assuming standard information is always 1

        similarity = 0
        for _, row in context.iterrows():
            obj_a = row[feature_a]
            obj_b = row[feature_b]
            similarity += calculate_similarity(obj_a, obj_b, omega)

        contextual_similarity_matrix[i][j] = similarity

contextual_similarity_matrix /= len(context) # Normalising data

context_df=pd.DataFrame(contextual_similarity_matrix)

context_df

U, Sigma, VT = np.linalg.svd(context_df)
k = 2
S = U[:, :k]

S.shape

import numpy as np

alpha = 0.0001   # learning rate
beta = 0.04# regularisation parameter
lmbda = 0.09    # momentum parameter

# Corrected function call to initialize P_Q_t with zeros
P_Q_t = np.zeros((1620, 249))

# function for rui_cap
def r_predicted(mean_rating, b_u, b_i, P_matrix, Q_t, u, i):
    P_Q_t = np.dot(P_matrix, Q_t)
    rui_cap = mean_rating + b_u + b_i + P_Q_t[u][i]
    return rui_cap

# function to calculate error
def err(rui, rui_cap):
    return rui - rui_cap

# bias_user updating function
def upd_bias_u(prev_b_u, alpha, beta, err_ui):
    return prev_b_u + alpha * (err_ui - (beta * prev_b_u))

# bias_item updating function
def upd_bias_i(prev_b_i, alpha, beta, err_ui):
    return prev_b_i + alpha * (err_ui - (beta * prev_b_i))

# P_u updation (updating user_feature_matrix one row at a time)
def upd_P_u(lmbda, prev_P_u, alpha, err_ui, Q_i, beta, u, i):
    return lmbda * prev_P_u[i] + (alpha * (err_ui * Q_i[i] - beta * prev_P_u[u]))


# Q_i updation (updating item_feature_matrix one column at a time)
def upd_Q_i(lmbda, prev_P_u, alpha, err_ui, Q_i, beta, u, i):
    return lmbda * Q_i[i] + (alpha * (err_ui * prev_P_u[u] - beta * Q_i[i]))

P_u=0
Q_i=0
P_u= user_feature_matrix.to_numpy()
Q_i= item_property_matrix.to_numpy()
P_u.dtype
P_u=P_u[:,1:]
Q_i=Q_i[:,1:]
P_u.shape
Q_i.shape
# b_i.shape
P_u

import numpy as np
import math

# intial b_u , b_i
# things to do : initial b_u & b_i values have to be made

PQ_t = np.dot(user_feature_matrix,item_property_matrix.transpose())
mean_rating = np.mean(A_df)
b_u = np.zeros(1620)
b_i = np.zeros(249)
sum_u=0
sum_i=0
for i in range(1620):
  for j in range(249):
      sum_u= sum_u + (A_df[i][j]-mean_rating)
  b_u[i]=sum_u/249


for j in range(249):
  for i in range(1620):
      sum_i= sum_i + (A_df[i][j]-mean_rating)
  b_i[j]=sum_i/1620

# b_i=sum_i/249
# b_u=sum_u/1620


# # initial prediction
# rui_cap = r_predicted(mean_rating, b_u, b_i, user_feature_matrix, item_property_matrix.transpose())




# Define the dimensions of the A_matrix
rows = 1295
columns = 199

# Initialize a A_matrix filled with zeros
A_cap_matrix = np.zeros((1620,249))

for u in range(rows):
    for i in range(columns):

    # step 1 rui_cap
      rui_cap = r_predicted(mean_rating, b_u[u], b_i[i],P_u , Q_i.transpose(),u,i)
      A_cap_matrix[u][i] = rui_cap

    # step 2 error
      err_ui = np.abs(err(A_df[u][i], rui_cap))
      print(err_ui)

    # bias for user updation
    # b_u[u] = upd_bias_u(b_u[u], alpha, beta, err_ui)

    # bias for item updation
    # if ( i < 249):
      b_i[i] = upd_bias_i(b_i[i], alpha, beta, err_ui)
      # b_u[u] = upd_bias_u(b_u[u], alpha, beta, err_ui)
      # P_u[u] = upd_P_u(lmbda, P_u, alpha, err_ui, Q_i, beta, u, i)
      print(f"{P_u[u]} user {u} ")
      Q_i[i] = upd_Q_i(lmbda, P_u, alpha, err_ui, Q_i , beta,u,i)
      print(f"{Q_i[i]} item {i}")   # Q_i
    b_u[u] = upd_bias_u(b_u[u], alpha, beta, err_ui)
    P_u[u] = upd_P_u(lmbda, P_u, alpha, err_ui, Q_i, beta, u, i)

b_u_initial=b_u
b_i_initial=b_i
    # user_feature_matrix=user_feature_matrix[:,1:]
      # b_u[u] = upd_bias_u(b_u[u], alpha, beta, err_ui)
      # P_u[u] = upd_P_u ( lmbda, P_u, alpha, err_ui, Q_i, beta, u, i)
  #  b_u[u] = upd_bias_u(b_u[u], alpha, beta, err_ui)
    # if ( i < 249):
    # Q_i[i] = upd_Q_i ( lmbda, P_u, alpha, err_ui, Q_i , beta,u,i)    # Q_i

P_u

A_cap_matrix

data_std = np.std(A_cap_matrix)

data_standardized = (A_cap_matrix - np.mean(A_df)) / data_std
A_cap_matrix = data_standardized*5

print(np.mean(A_df))

for u in range(1620):
  for i in range(198,249):
    A_cap_matrix[u][i]=r_predicted(mean_rating, b_u[u], b_i[i],P_u , Q_i.transpose(),u,i)

for u in range(1294,1620):
  for i in range(249):
        A_cap_matrix[u][i]=r_predicted(mean_rating, b_u[u], b_i[i],P_u , Q_i.transpose(),u,i)

# Evaluation
rmse = 0.0

for u in range(1620):
  for i in range(249):
    rmse += np.square(ratings_df[u][i] - A_cap_matrix[u][i])

rmse1 = rmse / (1620 * 249)
rmse_root2 = np.sqrt(rmse1)

rmse_root2

#precision
correct = 0.0
number=0
visited_number=0
visited=np.zeros((1620,249))
for u in range(1295,1620):
  for i in range(249):
    visited[u][i]=1
    if(A_matrix[u,i]>0 and A_cap_matrix[u,i]>0):
      # if (abs(A_matrix[u][i]-A_cap_matrix[u][i]) <0.2):
      if (A_matrix[u][i] - 0.1 <= A_cap_matrix[u][i] and A_cap_matrix[u][i]<= A_matrix[u][i] + 0.1):
       correct = correct + 1
      # visited[u,i]=1
      visited_number=visited_number+1
# for u in range(1620):
#   for i in range(199,249):
#    if visited[u][i]!=1:
#     visited_number=visited_number+1
#     visited[u][i]=1
#     if (abs(A_matrix[u][i]-A_cap_matrix[u][i]) <0.2):
#        correct = correct + 1


precision = 0.0
precision = correct /(visited_number)
print(visited_number)
print(correct)
print(precision)
print(visited)

import tensorflow as tf
import numpy as np
import pandas as pd

# Dummy data for example purposes
class CollaborativeFilteringModel(tf.keras.Model):
    def __init__(self, num_users, num_items, latent_dim):
        super(CollaborativeFilteringModel, self).__init__()
        self.user_embedding = tf.keras.layers.Embedding(num_users, latent_dim)
        self.item_embedding = tf.keras.layers.Embedding(num_items, latent_dim)

    def call(self, inputs):
        user_ids, item_ids = inputs
        user_latent = self.user_embedding(user_ids)  # Shape: (num_users, latent_dim)
        item_latent = self.item_embedding(item_ids)  # Shape: (num_items, latent_dim)
        # Compute dot product to get predicted ratings
        return tf.matmul(user_latent, item_latent, transpose_b=True)  # Shape: (num_users, num_items)

# Parameters
latent_dim = 50  # Dimensionality of the latent space
learning_rate = 0.01
num_epochs = 10

# Initialize model
num_users = 1295
num_items = 249
model = CollaborativeFilteringModel(num_users, num_items, latent_dim)

# Define optimizer
optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)

# Define loss function
loss_fn = tf.keras.losses.MeanSquaredError()

# Training loop
for epoch in range(num_epochs):
    with tf.GradientTape() as tape:
        user_ids = tf.range(num_users)
        item_ids = tf.range(num_items)
        # user_ids = tf.expand_dims(user_ids, axis=-1)
        # item_ids = tf.expand_dims(item_ids, axis=-1)

        # Predict ratings for all user-item pairs
        predicted_ratings = model([user_ids, item_ids])

        # Compute loss over all ratings
        mask = A_df[:1295,:] != 0  # Mask for non-zero ratings
        loss = loss_fn(tf.boolean_mask(A_df[:1295,:], mask), tf.boolean_mask(predicted_ratings, mask))

    # Backpropagation
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))

    total_loss = loss.numpy()
    print("Epoch {}: Loss: {}".format(epoch + 1, total_loss))

    # Optionally, print or store the predicted ratings matrix
    print(predicted_ratings.numpy())

validation_data_users = A_df[1295:1620, :]  # Validation for remaining users with first 199 items
# validation_data_items = A_df[1295:1620, 199:249]  # Validation for remaining items with first 1295 users

# Step 3: Compute Predictions
user_ids_validation = tf.range(validation_data_users.shape[0])
item_ids_validation = tf.range(validation_data_users.shape[1])
predicted_ratings_validation_users = model([user_ids_validation, item_ids_validation])

# user_ids_validation_items = tf.range(validation_data_items.shape[0])
# item_ids_validation_items = tf.range(validation_data_items.shape[1])
# predicted_ratings_validation_items = model([user_ids_validation_items, item_ids_validation_items])

predicted_ratings_validation_users.shape

#precision
correct = 0.0
visited_number =0.0
for u in range(325):
  for i in range(249):
   if(validation_data_users[u,i]>0):
    visited_number = visited_number +1

    # if (abs(validation_data_users[u][i]-predicted_ratings_validation_users[u][i])<1):
    if (validation_data_users[u][i] - 0.1 <= predicted_ratings_validation_users[u][i] and predicted_ratings_validation_users[u][i]<= validation_data_users[u][i] + 0.1):

      correct = correct + 1


# for u in range(325):
#   for i in range(50):
#     if (abs(validation_data_items[u][i]-predicted_ratings_validation_items[u][i]) <=0.1):
#       correct = correct + 1
precision = 0.0
precision = correct /(visited_number)
print(correct)
print(precision)

"""## CSSVD"""

P_u=0
Q_i=0
P_u= user_feature_matrix.to_numpy()
Q_i= item_property_matrix.to_numpy()
P_u.dtype
P_u=P_u[:,1:]
Q_i=Q_i[:,1:]
P_u.shape
Q_i.shape
# b_i.shape
P_u

Q_i

S

ruic = np.zeros((1620,249,14))
k_features=2
for u in range(1620):
    for i in range(249):
        for c in range(14):
         for k_idx in range(k_features):
        # Extract the k-th feature from P_u, S, and Q_i
          P_u_k = P_u[u][k_idx]
          S_k = S[c][k_idx]
          Q_i_k = Q_i[i][k_idx]

        # Element-wise multiplication
          temp = P_u_k * S_k * Q_i_k
          # print(temp)
        # Accumulate the result
          ruic[u,i,c]+= temp

P_u

ruic

"""### SGD for CSSVD"""

import numpy as np

def ruic_func(P_u, S, Q_i, k_features, u, i, c):
    # Get the shape of the input matrices
    n_rows, n_cols = S.shape
    n_depth = Q_i.shape[0]

    ruic_temp = np.zeros((1620,249,14))

    for k_idx in range(k_features):
        # Extract the k-th feature from P_u, S, and Q_i
        P_u_k = P_u[u, k_idx]
        S_k = S[c, k_idx]
        Q_i_k = Q_i[i, k_idx]

        # Element-wise multiplication
        temp = P_u_k * S_k * Q_i_k

        # Accumulate the result
        ruic_temp[u,i,c]+= temp

    return ruic_temp[u,i,c]





# Function to calculate ruic_cap
def ruic_predicted(mean_rating, b_u, b_i, b_c, ruic, u, i, c):
    return mean_rating + b_u[u] + b_i[i] + b_c[c] + ruic[u, i, c]

# Function to calculate error
def err_uic(ruic, ruic_cap):
    return ruic - ruic_cap

# Function to update bias_user
def upd_bias_u(prev_b_u, alpha, beta, err_uic):
    return prev_b_u + alpha * (err_uic - (beta * prev_b_u))

# Function to update bias_item
def upd_bias_i(prev_b_i, alpha, beta, err_uic):
    return prev_b_i + alpha * (err_uic - (beta * prev_b_i))

# Function to update bias_context
def upd_bias_c(prev_b_c, alpha, beta, err_uic):
    return prev_b_c + alpha * (err_uic - (beta * prev_b_c))

# Function to update P_u
def upd_P_u(lmbda, prev_P_u, alpha, err_uic, Q_i, S, beta, u, i, c):
    return lmbda * prev_P_u[u] + (alpha * (err_uic * Q_i[i] * S[c] - beta * prev_P_u[u]))

# Function to update Q_i
def upd_Q_i(lmbda, prev_Q_i, alpha, err_uic, P_u, S, beta, u, i, c):
    return lmbda * prev_Q_i[i] + (alpha * (err_uic * P_u[u] * S[c] - beta * prev_Q_i[c]))

# Function to update S_c
def upd_S_c(lmbda, prev_S_c, alpha, err_uic, P_u, Q_i, beta, u, i, c):
    return lmbda * prev_S_c[c] + (alpha * (err_uic * P_u[u] * Q_i[i] - beta * prev_S_c[c]))

# Main code starts here
alpha = 0.0001
beta = 0.04
lmbda = 0.09
k_features = 2

# Initialize biases and other matrices
b_u = np.zeros(1620)
b_i = np.zeros(249)
b_c = np.zeros(14)
ruic_cap = np.zeros((1620, 249, 14))
ruic_temp = np.zeros((1620,249, 14))


# Calculate mean ratings
mean_rating = np.mean(A_df)

# Calculate biases
for i in range(1620):
    b_u[i] = np.mean(A_df[i, :]) - mean_rating
for j in range(249):
    b_i[j] = np.mean(A_df[:, j]) - mean_rating
for k in range(14):
    b_c[k] = np.mean(S[k, :k_features]) - np.mean(S)

# Perform iterations
for u in range(1295):
    for i in range(199):
        for c in range(14):
            ruic_temp[u,i,c] = ruic_func(P_u, S, Q_i, k_features, u, i, c)
            ruic_cap[u, i, c] = ruic_predicted(mean_rating, b_u, b_i, b_c, ruic_temp, u, i, c)
            error_uic = err_uic(ruic[u, i, c], ruic_cap[u, i, c])
            # print(error_uic)
            b_c[c] = upd_bias_c(b_c[c], alpha, beta, error_uic)
            S[c] = upd_S_c(lmbda, S, alpha, error_uic, P_u, Q_i, beta, u, i, c)
            # Update biases
            # b_u[u] = upd_bias_u(b_u[u], alpha, beta, error_uic)
        b_i[i] = upd_bias_i(b_i[i], alpha, beta, error_uic)
            # b_c[c] = upd_bias_c(b_c[c], alpha, beta, error_uic)
        Q_i[i] = upd_Q_i(lmbda, Q_i, alpha, error_uic, P_u, S, beta, u, i, c)
            # Update P, Q, S
    b_u[u] = upd_bias_u(b_u[u], alpha, beta, error_uic)
    P_u[u] = upd_P_u(lmbda, P_u, alpha, error_uic, Q_i, S, beta, u, i, c)
            # Q_i[i] = upd_Q_i(lmbda, Q_i, alpha, error_uic, P_u, S, beta, u, i, c)
            # S[c] = upd_S_c(lmbda, S, alpha, error_uic, P_u, Q_i, beta, u, i, c)

ruic_cap

for u in range(1620):
  for i in range(198,249):
    for c in range(14):
            ruic_temp[u,i,c] = ruic_func(P_u, S, Q_i, k_features, u, i, c)
            ruic_cap[u, i, c] = ruic_predicted(mean_rating, b_u, b_i, b_c, ruic_temp, u, i, c)

for u in range(1294,1620):
  for i in range(249):
    for c in range(14):
            ruic_temp[u,i,c] = ruic_func(P_u, S, Q_i, k_features, u, i, c)
            ruic_cap[u, i, c] = ruic_predicted(mean_rating, b_u, b_i, b_c, ruic_temp, u, i, c)

ruic_cap

"""# Evaluaion for *CSSVD*"""

correct = 0.0
number=0
visited_number=0
visited=np.zeros((1620,249))
positives=0
for u in range(1295,1620):
  for i in range(249):
    for c in range(14):
    # visited[u][i]=1
     if(ruic[u,i,c]>0):
      if (abs((ruic_cap[u][i][c])-(ruic[u][i][c]))<0.1):
       correct = correct + 1
      # visited[u,i]=1
      visited_number=visited_number+1
# for u in range(1620):
#   for i in range(199,249):
#    if visited[u][i]!=1:
#     visited_number=visited_number+1
#     visited[u][i]=1
#     if (abs(A_matrix[u][i]-A_cap_matrix[u][i]) <0.5):
#        correct = correct + 1


precision = 0.0
precision = correct /(visited_number)
print(visited_number)
print(f"total is {325*249*14} ")
print(correct)
print(precision)

