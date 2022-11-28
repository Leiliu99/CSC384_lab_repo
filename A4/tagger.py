# The tagger.py starter code for CSC384 A4.
# Currently reads in the names of the training files, test file and output file,
# and calls the tagger (which you need to implement)
import os
import sys
# intitial, transition, emission matrix
I = []
T = []
M = []
#record each word, tag's location in the above matrix
#key:word/tag(string), value: position in matrix
word_to_loc = {}
tag_to_loc = {}
loc_to_tag = {}
new_word_pointer = 0
new_tag_pointer = 0

#recod each tag's total number
#key: tag's position, value: total number of this tag
tagloc_to_number = {}

#record the total number of word, tag types
#so that we can decide the size of I,T,M
total_word = 0
total_tag = 0

#store the word and tag itself separately in two lists
#[[word sequence in training 1], [word sequence in training 2]]
word_queue = []
tag_queue = []


def debug_location():
    print("----------test word's location-----------")
    print(word_to_loc)
    print("\n")
    print("----------test tag's location-----------")
    print(tag_to_loc)
    print("\n")
    # print("----------test each tag's total number-----------")
    # print(tagloc_to_number)
    # print("\n")
    # print("----------test word queue-----------")
    # print(word_queue)
    # print("\n")
    # print("----------test tag queue-----------")
    # print(tag_queue)
    # print("\n")
    print("total word is: " + str(total_word))
    print("total tag is: " + str(total_tag))

def debug_matrix():
    print("----------check I size----------")
    print(len(I))
    print(I)
    print("----------check T size----------")
    print("row size: " + str(len(T)) + " col size: " + str(len(T[0])))
    print("----------check M size----------")
    print("row size: " + str(len(M)) + " col size: " + str(len(M[0])))

    print(I)
    print(T)
    print(M)


def training(training_list):
    # take in the training file,
    # recognize word and tag separately
    # prepare the I, T, M matrix from the training data
    global I
    global T
    global M
    global word_to_loc
    global tag_to_loc
    global loc_to_tag
    global new_word_pointer
    global new_tag_pointer
    global total_word
    global total_tag
    global word_queue
    global tag_queue

    for training_file in training_list:
        training_read = open(training_file, 'r')
        training_string = training_read.read()
        training_read.close()
        intermediate_string = training_string.split("\n")
        test_i = 0
        training_words = []
        training_tags = []

        for string_pair in intermediate_string:
            if string_pair == "":
                print("----------parsed the end of this training file----------")
                continue
            word, tag = string_pair.split(" : ")
            # print (word)
            if not word in word_to_loc:
                word_to_loc[word] = new_word_pointer
                new_word_pointer += 1
                total_word += 1
            training_words.append(word)
            # print (tag)
            if not tag in tag_to_loc:
                tag_to_loc[tag] = new_tag_pointer
                loc_to_tag[new_tag_pointer] = tag
                tagloc_to_number[new_tag_pointer] = 1
                new_tag_pointer += 1
                total_tag += 1
            else:
                tagloc_to_number[tag_to_loc[tag]] += 1 #increment by 1
            training_tags.append(tag)
            test_i += 1
            # if test_i == 5:
            #     break
        assert len(training_words) == len(training_tags)
        word_queue.append(training_words)
        tag_queue.append(training_tags)

    # debug_location()
    #prepare matrix
    I.extend([0] * total_tag)
    T = [[0]* total_tag for i in range(total_tag)] #row:tag, col: tag
    M = [[0]* total_word for i in range(total_tag)] #row:tag, col: word

    #------I------
    for loc,number in tagloc_to_number.items():
        I[loc] = number
    # print(I)
    #normalize I
    I_normalization_constant = sum(I)
    for i, element in enumerate(I):
        I[i] = element/I_normalization_constant
    # print(I)
    # ------T and M------
    for train_order, word_list in enumerate(word_queue):
        for i, start_word in enumerate(word_list):
            start_pos = word_to_loc[start_word]
            tag_pos = tag_to_loc[tag_queue[train_order][i]]
            M[tag_pos][start_pos] += 1
            if i == len(word_list) - 1:
                continue #last one, no need to evaluate
            if start_word == "." or start_word == "?" or start_word == "!":
                continue #terminate word, no need to evaluate for transition
            tag_end = tag_to_loc[tag_queue[train_order][i + 1]]
            T[tag_pos][tag_end] += 1

    # normalize T and M
    # print(T)
    for i, row in enumerate(T):
        T_normalization_constant = sum(row)
        for j, col in enumerate(row):
            if col == 0:
                continue
            T[i][j] = col / T_normalization_constant
    # print(T)
    # print(M)
    for i, row in enumerate(M):
        M_normalization_constant = sum(row)
        for j, col in enumerate(row):
            if col == 0:
                continue
            M[i][j] = col / M_normalization_constant
    # print(M)
    #debug_matrix()

def prepare_viterbi(test_file, word_result, tag_result):
    global word_to_loc
    testing_read = open(test_file, 'r')
    testing_string = testing_read.read()
    testing_read.close()
    intermediate_string = testing_string.split("\n")
    # print(intermediate_string)
    valid_sentence = []
    for word in intermediate_string:
        if word == "":
            print("----------the end of testing file-----------")
            break
        if not word in word_to_loc:
            print("-----------not seen in training!-----------")
            return
        valid_sentence.append(word)
        word_result.append(word)
        if word == "." or word == "?" or word == "!": #symbol of terminating a sentence
            # print(valid_sentence)
            sentence_tag = viterbi(valid_sentence)
            tag_result.extend(sentence_tag)
            valid_sentence = []
    if not len(valid_sentence) == 0:
        print("----------no termination at the end-----------")
        # print(valid_sentence)
        sentence_tag = viterbi(valid_sentence)
        tag_result.extend(sentence_tag)

    # test = []
    # for tag_loc in tag_out:
    #     test.append(loc_to_tag[tag_loc])
    # print(tag_out)
    # print(test)
    # return word_out, tag_out

def viterbi(untagged_sentence):
    global I
    global M
    if len(untagged_sentence) == 0:
        print("----------empty sentence for viterbi-----------")
        return
    length_E = len(untagged_sentence)
    prob = [[0] * total_tag for i in range(length_E)]  # row:length of word(E), col: tag
    prev = [[0] * total_tag for i in range(length_E)]  # row:length of word(E), col: tag

    # determine values for the first word in the sentence
    for i in range(total_tag):
        prob[0][i] = I[i] * M[i][word_to_loc[untagged_sentence[0]]]
        prev[0][i] = None

    # for the second word to the last word in sentence
    # find each current state's most likely prior state x

    for word_t in range(1, length_E):
        word_loc = word_to_loc[untagged_sentence[word_t]]
        for tag_i in range(total_tag):
            max_prob = 0
            max_index = -1
            for pre_tag_i in range(total_tag):
                current_prob = prob[word_t - 1][pre_tag_i] * T[pre_tag_i][tag_i] * M[tag_i][word_loc]
                if current_prob > max_prob:
                    max_prob = current_prob
                    max_index = pre_tag_i
            prob[word_t][tag_i] = max_prob
            prev[word_t][tag_i] = max_index

    #find the largest prob for the last word
    last_word = length_E - 1
    final_prob = 0
    final_tag = -1
    for tag_i in range (total_tag):
        current = prob[last_word][tag_i]
        if current > final_prob:
            final_prob = current
            final_tag = tag_i

    tag_path = []
    while not last_word == -1:
        # print("last word is: " + str(last_word) + "final_tag is: " + str(final_tag))
        tag_path.append(final_tag)
        prev_tag = prev[last_word][final_tag]
        # tag_path.append(prev_tag)
        final_tag = prev_tag
        last_word -= 1
    tag_path.reverse() # reverse path to start from initial tag
    return tag_path

def write_output(word_result, tag_result, output_file):
    assert (len(word_result) == len(tag_result))
    if len(word_result) == 0:
        return
    with open(output_file, 'a') as f:
        f.truncate(0)
        for i, word in enumerate(word_result):
            f.write(word)
            f.write(" : ")
            f.write(loc_to_tag[tag_result[i]])
            f.write('\n')



def tag(training_list, test_file, output_file):
    # Tag the words from the untagged input file and write them into the output file.
    # Doesn't do much else beyond that yet.
    print("Tagging the file.")
    #
    # YOUR IMPLEMENTATION GOES HERE
    #
    training(training_list)
    word_result = []
    tag_result = []
    prepare_viterbi(test_file, word_result, tag_result)
    write_output(word_result, tag_result, output_file)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training files> -t <test file> -o <output file>"
    parameters = sys.argv
    training_list = parameters[parameters.index("-d")+1:parameters.index("-t")]
    test_file = parameters[parameters.index("-t")+1]
    output_file = parameters[parameters.index("-o")+1]
    print("Training files: " + str(training_list))
    print("Test file: " + test_file)
    print("Output file: " + output_file)

    # Start the training and tagging operation.
    tag (training_list, test_file, output_file)