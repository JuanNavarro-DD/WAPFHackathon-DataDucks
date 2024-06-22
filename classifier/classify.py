
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import pandas as pd
import spacy_sentence_bert
from sklearn.metrics import accuracy_score
import pickle


def load_data(fp):
    '''
    Load the training data and return a dataframe
    '''
    with open(fp, 'r') as infile:
        df = pd.read_csv(infile)
    return df


def create_model(df, data_col):
    '''
    Vectorise and split the data. Expecting the data to have two columns, Label and transcription 
    Create and train a basic SVM for classifying data.
    Pass in the Split vector data
    '''
    #TODO: Error handling
    
    nlp = spacy_sentence_bert.load_model('en_stsb_distilbert_base') #TODO look at multi language models
    df['vector'] = df[data_col].apply(lambda x: nlp(x).vector)

    X_train, X_test, y_train, y_test = train_test_split(df['vector'].tolist(), df[data_col].tolist(), test_size=0.33, random_state=127)


    clf = SVC(gamma='auto')
    clf.fit(X_train, y_train)

    #Basic Test
    y_pred = clf.predict(X_test)
    print(f"Baseline Accuracy{accuracy_score(y_test, y_pred)}")

    with open('svm_classifier.pkl', 'wb') as outfile:
        pickle.dump(clf,outfile)

    print("Written model")



if __name__ == '__main__':
    print("Generating model")
    df = load_data("train_data.csv")
    create_model(df, 'transcription')