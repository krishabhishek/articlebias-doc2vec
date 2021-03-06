from utils import file_helper, doc2vec_helper
from utils import scikit_ml_helper

from processors.processor import Processor
from utils import log_helper

log = log_helper.get_logger("AmazonLineProcessor")


class AmazonLineProcessor(Processor):

    def __init__(self, labeled_articles_source_file_path, doc2vec_model_file_path, ml_model_file_path,
                 articles_source_file_path, shuffle_count, classification_sources_file_path):
        self.labeled_articles_file_path = labeled_articles_source_file_path
        self.articles_source_file_path = articles_source_file_path
        self.doc2vec_model_file_path = doc2vec_model_file_path
        self.ml_model_file_path = ml_model_file_path
        self.shuffle_count = shuffle_count
        self.classification_sources_file_path = classification_sources_file_path

    def process(self):

        log.info("Commencing execution")

        combined_iterator = file_helper.get_reviews_iterator(self.classification_sources_file_path)

        sentences = []
        doc_count = 0
        for tagged_doc in combined_iterator:
            doc_count += 1
            sentences.append(tagged_doc)

        doc2vec_model = doc2vec_helper.init_model(sentences)
        log.info("Learnt vocab from training set")

        # saving the doc2vec model to disk
        doc2vec_model.save(self.doc2vec_model_file_path)

        # Extracting parameters for and training the ML model
        x_docvecs, y_scores = doc2vec_helper.extract_classification_parameters(doc2vec_model, doc_count)


        log.info("Training the ML models")
        ml_model_logreg = scikit_ml_helper.train_logistic_reg_classifier(x_docvecs, y_scores)
        ml_model_nb = scikit_ml_helper.train_gnb_classifier(x_docvecs, y_scores)
        ml_model_svm_linear = scikit_ml_helper.train_svm_classifier(x_docvecs, y_scores)

        log.info("Saving the ML models to disk")
        scikit_ml_helper.persist_model_to_disk(ml_model_logreg, self.ml_model_file_path + ".docvec.log_reg")
        scikit_ml_helper.persist_model_to_disk(ml_model_nb, self.ml_model_file_path + ".docvec.nb")
        scikit_ml_helper.persist_model_to_disk(ml_model_svm_linear, self.ml_model_file_path + ".docvec.svm_linear")

        log.info("Completed execution")
