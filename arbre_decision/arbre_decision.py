import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.tree import export_graphviz
import graphviz
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

# Function to load data from a CSV file
def load_data(file_path):
    data = pd.read_csv(file_path, delimiter='\t')
    #print(data.dtypes)  # Uncomment this line to print data types of columns in the loaded dataset
    return data

# Function for one-hot encoding of categorical columns in the dataset
def one_hot_encoder(data):
    # # For F0 
    # numeric_columns = ['MeanGlobal', 'MeanLocal', 'MeanNormalized', 'SemitonFromUtterance']
    numeric_columns = ['SemitonFromUtterance']

    # # For duration
    # numeric_columns = ['DurationGlobal', 'DurationLocal', 'DurationNormalized']
    # numeric_columns = ['DurationNormalized']

    # # For F0 and duration
    # numeric_columns = ['MeanGlobal', 'MeanLocal', 'MeanNormalized', 'SemitonFromUtterance', 'DurationGlobal', 'DurationLocal', 'DurationNormalized']
    # numeric_columns = ['MeanGlobal', 'MeanLocal', 'MeanNormalized', 'SemitonFromUtterance', 'DurationGlobal', 'DurationLocal', 'DurationNormalized']
    
    features = pd.concat([data[numeric_columns]], axis=1)

    # labels = data['POS'] # for GoAux-GoVerb and DeyAux-DeyVerb
    labels = data['Form'] # for Sey-Say

    return features, labels

# Function to train a decision tree classifier
def train_decision_tree(features, labels, max_depth):
    X_train, X_test, y_train, y_test = train_test_split(features, labels, stratify=labels, test_size=0.5)
    model = DecisionTreeClassifier(criterion='entropy', max_depth=None)  # Initialize the decision tree model
    best_val_accuracy = 0.0
    best_model = None

    # Loop through different depths to find the best decision tree model
    for depth in range(1, max_depth + 1):
        model.set_params(max_depth=depth)  # Set the max depth for the model
        model.fit(X_train, y_train)  # Train the model with the current depth
        val_accuracy = model.score(X_test, y_test)  # Calculate validation accuracy
        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            best_model = model
            test_accuracy = best_model.score(X_test, y_test)  # Calculate test accuracy for the best model
    print("Best Model - Validation Accuracy:", best_val_accuracy)
    print("Best Model - Test Accuracy:", test_accuracy)
    return model, X_test, y_test

# Function to evaluate the trained model
def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)  # Make predictions on the test set
    report = classification_report(y_test, predictions)  # Generate classification report

    # # for GoAux-GoVerb and DeyAux-DeyVerb
    # confusion = confusion_matrix(y_test, predictions, labels=["AUX", "VERB"])  # Generate confusion matrix
    # columns = ["AUX_predicted", "VERB_predicted"]
    # index = ["AUX_actual", "VERB_actual"]

    # for Sey-Say
    confusion = confusion_matrix(y_test, predictions, labels=["sey", "say"])  # Generate confusion matrix
    columns = ["SEY_predicted", "SAY_predicted"]
    index = ["SEY_actual", "SAY_actual"]

    confusion_df = pd.DataFrame(confusion, columns=columns, index=index)
    accuracy = model.score(X_test, y_test)  # Calculate accuracy

    return report, confusion_df, accuracy

# Function to export the decision tree model graph
def export_model_graph(model, features):
    dot_data = export_graphviz(model, out_file=None, feature_names=features.columns, class_names=model.classes_,
                               filled=True, rounded=True)
    graph = graphviz.Source(dot_data)
    # graph.view("./TSV/ArbreDecision/GoAux-GoVerb/graphs_duration_f0/go_aux-go_verb-entropy_4_MNormalized_DNormalized")  # Change the output path if needed
    # graph.view("./TSV/ArbreDecision/DeyAux-DeyVerb/graphs_duration_f0/dey_aux-dey_verb-entropy_4") 
    graph.view("./TSV/ArbreDecision/Sey-Say/graphs_f0/sey_say-entropy_4_SemitonFromUtterance") 

# Function to save evaluation results to a text file
def save_results(report, confusion_df, accuracy):
    # output_path = "./TSV/ArbreDecision/GoAux-GoVerb/txt_duration_f0/go_aux-go_verb-entropy_4_MNormalized_DNormalized.txt"  # Change the output path if needed
    # output_path = "./TSV/ArbreDecision/DeyAux-DeyVerb/txt_duration_f0/dey_aux-dey_verb-entropy_4.txt"
    output_path = "./TSV/ArbreDecision/Sey-Say/txt_f0/sey_say-entropy_4_SemitonFromUtterance.txt"
    with open(output_path, "w") as file:
        file.write("Report:\n")
        file.write(report)
        file.write("\n\n")
        file.write("Confusion Matrix:\n")
        file.write(str(confusion_df))
        file.write("\n\n")
        file.write(f"Model Accuracy: {accuracy}\n\n")

    print("Report:")
    print(report)
    print("\nConfusion Matrix:")
    print(confusion_df)
    print(f"\nModel Accuracy: {accuracy}\n")

# Output TSV file path
# input_tsv = './TSV/ArbreDecision/GoAux-GoVerb/arbre_decision_go_aux-go_verb_filtre.tsv'
# input_tsv = './TSV/ArbreDecision/DeyAux-DeyVerb/arbre_decision_dey_aux-dey_verb_filtre.tsv'
input_tsv = './TSV/ArbreDecision/Sey-Say/arbre_decision_sey_say_filtre.tsv'


# Load the data from the TSV file
data = load_data(input_tsv)

# Drop rows with missing values (NaN)
data.dropna(inplace=True)

# One-hot encode the categorical columns and prepare features and labels for training
features, labels = one_hot_encoder(data)

# Train the decision tree model with a maximum depth of 4
model, X_test, y_test = train_decision_tree(features, labels, max_depth=4)

# Evaluate the trained model
report, confusion_df, accuracy = evaluate_model(model, X_test, y_test)

# Export the decision tree model graph
export_model_graph(model, features)

# Save evaluation results to a text file
save_results(report, confusion_df, accuracy)
