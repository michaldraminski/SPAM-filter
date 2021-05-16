import numpy as np
import glob
import string
from xml.dom import minidom
from stempel import StempelStemmer

class Mail:
    # konstruktor domyślny
    def __init__(self, nadawca='', odbiorca='', data='', tytul='', tresc='', isspam=-1):
        self.nadawca = nadawca
        self.odbiorca = odbiorca
        self.data = data
        self.tytul = tytul
        self.tresc = tresc
        self.isspam = isspam

    # metoda do wyświetlania maila
    def show_mail(self):
        print("\n" + self.data.strip())
        print(self.tytul.strip())
        print(self.tresc.strip() + "\n")

    # metoda do wczytywania maila do zmiennych klasowych
    def read_mail(self, lines, name):
        for line in lines:
            if name.find("spam") != -1:
                self.isspam = 1
            elif name.find("ham") != -1:
                self.isspam = 0
            content = line.split(":", 1)[1].lstrip()
            info = line.split(":", 1)[0].strip()
            if info == "odpowiedz do":
                self.nadawca = content
            elif info == "do":
                self.odbiorca = content
            elif info == "data":
                self.data = content
            elif info == "temat":
                self.tytul = content
            elif info.lower() == "treść":
                self.tresc = content.strip()

    # metoda rozbija tresc i tytuł maila na liste słów
    def split_to_words(self):
        words = [word.strip(string.punctuation).lower() for word in self.tresc.split()]
        words += [word.strip(string.punctuation).lower() for word in self.tytul.split()]
        return words


# funkcja zamienia listę słów na słownik z liczbą wystąpień i zwraca słownik i liczbę wszystkich słów
def list_to_dict(word_list,k):
    unique_words, counts = np.unique(word_list, return_counts=True)
    word_num = sum(counts)
    slownik = {unique_words[i]: counts[i]/(np.sum(counts)+k*2) for i in range(len(unique_words))}
    return slownik, word_num


# funkcja wyszukuje słowo i zwraca liczbę jego wystąpień
def find_instances_in_dict(word_wanted, dictionary):
    for word, instances in dictionary.items():
        if word == word_wanted:
            return instances
    return 0

#def merge_dictionaries()


# funkcja sprawdza, czy dany mail jest spamem
def is_spam(filename, spam_dict, ham_dict, PSPAM, PHAM, k):
    with open("./spam/" + filename) as example:
        message = Mail()
        lines = example.readlines()
        message.read_mail(lines, "example")
        word_list = message.split_to_words()
        message.show_mail()
        Pmess_ifSPAM = 1
        Pmess_ifHAM = 1
        for slowo in word_list:
            P_spam = find_instances_in_dict(slowo, spam_dict)
            P_ham = find_instances_in_dict(slowo, ham_dict)
            if P_spam != 0:
                Pmess_ifSPAM *= P_spam
            if P_ham != 0:
                Pmess_ifHAM *= P_ham
            # print(slowo, "𝑃(𝑤𝑜𝑟𝑑|𝑆𝑃𝐴𝑀): ", round(P_spam, 2), "  𝑃(𝑤𝑜𝑟𝑑|𝐻𝐴𝑀):", round(P_ham, 2))
        if Pmess_ifSPAM == 1:
            Pmess_ifSPAM = 0
        if Pmess_ifHAM == 1:
            Pmess_ifHAM = 0

        PSPAM_ifmess = (Pmess_ifSPAM * PSPAM)/(Pmess_ifSPAM * PSPAM + Pmess_ifHAM * PHAM)
        PHAM_ifmess = (Pmess_ifHAM * PHAM)/(Pmess_ifSPAM * PSPAM + Pmess_ifHAM * PHAM)
        return PSPAM_ifmess, PHAM_ifmess

# funkcja zwraca prawdopodobieństwo, że słowo jest spamem
def spam_and_ham_prob(spam_mess_num, ham_mess_num, k):
    PSPAM = (spam_mess_num + k) / ((spam_mess_num + ham_mess_num) + k * 2)
    PHAM = (ham_mess_num + k) / ((spam_mess_num + ham_mess_num) + k * 2)
    return PSPAM,PHAM


if __name__ == "__main__":
    all_spam_words = []
    all_ham_words = []
    ham_mess_num = 0
    spam_mess_num = 0
    mails =[]

    # Wczytywanie wszystkich plików txt
    for mail in glob.glob("./spam/*.txt"):
        # Tworzenie obiektu
        message = Mail()

        # sprawdzanie czy pik jest spamem czy hamem na podstawie nazwy pliku
        name = mail.strip(string.punctuation)
        name = name.split("\\")[1]

        # otwieranie i przekształcanie pliku
        with open(mail) as f:
            lines = f.readlines()
            message.read_mail(lines, name)
            if message.isspam == 1:
                all_spam_words += message.split_to_words()
                spam_mess_num += 1
            elif message.isspam == 0:
                all_ham_words += message.split_to_words()
                ham_mess_num += 1
        mails.append(message)

    # paskudny fragment kodu do wywoływania obliczeń probabilistycznych w różnych wersjach
    spam_dict, all_spam_words_count = list_to_dict(all_spam_words, 0)
    ham_dict, all_ham_words_count = list_to_dict(all_ham_words, 0)

    PHAM, PSPAM = spam_and_ham_prob(spam_mess_num, ham_mess_num, 0 )
    PSPAM_ifmess, PHAM_ifmess = is_spam("example.txt", spam_dict, ham_dict, PHAM, PSPAM, 0)
    print("Prawdopodobieństwo (bez wygładzania), że powyższa wiadomość to spam: ", PSPAM_ifmess)
    print("Prawdopodobieństwo,(bez wygładzania) że powyższa wiadomość to ham: ", PHAM_ifmess)

    PHAM, PSPAM = spam_and_ham_prob(spam_mess_num, ham_mess_num, 2 )
    PSPAM_ifmess, PHAM_ifmess = is_spam("example.txt", spam_dict, ham_dict, PHAM, PSPAM, 2)
    print("Prawdopodobieństwo (z użyciem wygładzania, k=2), że powyższa wiadomość to spam: ", PSPAM_ifmess)
    print("Prawdopodobieństwo,(z użyciem wygładzania, k=2) że powyższa wiadomość to ham: ", PHAM_ifmess)

    # Wczytanie xml'a i dodanie do słownika
    xmldoc = minidom.parse('./spam/dict.xml')
    xmlword = xmldoc.getElementsByTagName('word')

    for word in xmlword:
        if word.attributes['type'].value == 'spam':
            spam_dict[word.firstChild.nodeValue] = word.attributes['probabilty'].value
        if word.attributes['type'].value == 'ham':
            ham_dict[word.firstChild.nodeValue] = word.attributes['probabilty'].value

    spam_dict, all_spam_words_count = list_to_dict(all_spam_words, 2)
    ham_dict, all_ham_words_count = list_to_dict(all_ham_words, 2)
    PHAM, PSPAM = spam_and_ham_prob(spam_mess_num, ham_mess_num, 2)
    PSPAM_ifmess, PHAM_ifmess = is_spam("example.txt", spam_dict, ham_dict, PHAM, PSPAM, 2)
    print("Prawdopodobieństwo (z użyciem wygładzania, k=2) po połączeniu słowników, że powyższa wiadomość to spam: ", PSPAM_ifmess)
    print("Prawdopodobieństwo (z użyciem wygładzania, k=2) po połączeniu słowników, że powyższa wiadomość to ham: ", PHAM_ifmess)

    # zastosowanie StempelStemmer z odmianami polskich słów do inteligentnego słownika
    stempel = StempelStemmer
    stemmer = StempelStemmer.polimorf()
    smart_dict = {}

    # tworzenie nowego słownika przez z wystąpieniami słów pokrewnych
    for word in all_spam_words:
        w = stemmer.stem(word)
        if w in smart_dict:
            smart_dict[w] += 1
        else:
            smart_dict[w] = 1

    print("INTELIGENTY SŁOWNIK SPAMU:")
    print(smart_dict)

