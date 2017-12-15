import numpy as np

def create_embedding_matrix(we_file_path, max_nb_words, embedding_dim, word_list):
    
    # Indexing word vectors
    print('Indexing word vectors.')

    embeddings_index = {}
    f = open(we_file_path)
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()

    print('Found %s word vectors.' % len(embeddings_index))
    
    # Preparing embedding matrix
    print('Creating Word Embeddings matrix...')

    num_words = len(word_list) #min(MAX_NB_WORDS, len(word_index))
    embedding_matrix = np.zeros((num_words, embedding_dim))
    for word, i in word_list:
        if i >= max_nb_words:
            continue
        #embedding_vector = embeddings_index.get(word.encode('utf-8'))
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            embedding_matrix[i] = embedding_vector

    print('Word Embeddings matrix was successfuly created.')
            
    return embedding_matrix