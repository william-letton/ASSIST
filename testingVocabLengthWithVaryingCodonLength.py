punctuations = "`_çìëá•™©!£$€/%^&*+±=()â‰¥[]|0123456789'=.,:;?%<>ÿòñ~#@-—–{}úøîæ÷ó¬åà®¯§"+'"“”'

text = "Oh! But he was a tight-fisted hand at the grind-stone, Scrooge! a squeezing, wrenching, grasping, scraping, clutching, covetous, old sinner! Hard and sharp as flint, from which no steel had ever struck out generous fire; secret, and self-contained, and solitary as an oyster. The cold within him froze his old features, nipped his pointed nose, shrivelled his cheek, stiffened his gait; made his eyes red, his thin lips blue; and spoke out shrewdly in his grating voice. A frosty rime was on his head, and on his eyebrows, and his wiry chin. He carried his own low temperature always about with him; he iced his office in the dogdays; and didn't thaw it one degree at Christmas. External heat and cold had little influence on Scrooge. No warmth could warm, no wintry weather chill him. No wind that blew was bitterer than he, no falling snow was more intent upon its purpose, no pelting rain less open to entreaty. Foul weather didn't know where to have him. The heaviest rain, and snow, and hail, and sleet, could boast of the advantage over him in only one respect. They often `came down' handsomely, and Scrooge never did. Nobody ever stopped him in the street to say, with gladsome looks, `My dear Scrooge, how are you? When will you come to see me?' No beggars implored him to bestow a trifle, no children asked him what it was o'clock, no man or woman ever once in all his life inquired the way to such and such a place, of Scrooge. Even the blind men's dogs appeared to know him; and when they saw him coming on, would tug their owners into doorways and up courts; and then would wag their tails as though they said, `No eye at all is better than an evil eye, dark master!' But what did Scrooge care! It was the very thing he liked. To edge his way along the crowded paths of life, warning all human sympathy to keep its distance, was what the knowing ones call `nuts' to Scrooge."
no_punct=""
for character in text:
    if character not in punctuations:
        no_punct= no_punct+character
no_punct=no_punct.lower()

print("length of text: ",len(no_punct))
#print(no_punct)
## codon1
vocabulary=dict()
split=list()
for i in range(0,len(no_punct)):
    codon=no_punct[i]
    split.append(codon)
for word in split:
    vocabulary[word]=vocabulary.get(word,0)+1
#print("vocabulary: ",vocabulary)
print("vocabulary length: ",len(vocabulary))


##codon2
vocabulary=dict()
split=list()
for i in range(0,len(no_punct)-1):
    codon=no_punct[i]+no_punct[i+1]
    split.append(codon)
for word in split:
    vocabulary[word]=vocabulary.get(word,0)+1
#print("vocabulary: ",vocabulary)
print("vocabulary length: ",len(vocabulary))

##codon3
vocabulary=dict()
split=list()
for i in range(0,len(no_punct)-2):
    codon=no_punct[i]+no_punct[i+1]+no_punct[i+2]
    split.append(codon)
for word in split:
    vocabulary[word]=vocabulary.get(word,0)+1
#print("vocabulary: ",vocabulary)
print("vocabulary length: ",len(vocabulary))

##codon4
vocabulary=dict()
split=list()
for i in range(0,len(no_punct)-3):
    codon=no_punct[i]+no_punct[i+1]+no_punct[i+2]+no_punct[i+3]
    split.append(codon)
for word in split:
    vocabulary[word]=vocabulary.get(word,0)+1
#print("vocabulary: ",vocabulary)
print("vocabulary length: ",len(vocabulary))

##codon5
vocabulary=dict()
split=list()
for i in range(0,len(no_punct)-4):
    codon=no_punct[i]+no_punct[i+1]+no_punct[i+2]+no_punct[i+3]+no_punct[i+4]
    split.append(codon)
for word in split:
    vocabulary[word]=vocabulary.get(word,0)+1
#print("vocabulary: ",vocabulary)
print("vocabulary length: ",len(vocabulary))

##codon6
vocabulary=dict()
split=list()
for i in range(0,len(no_punct)-5):
    codon=no_punct[i]+no_punct[i+1]+no_punct[i+2]+no_punct[i+3]+no_punct[i+4]+no_punct[i+5]
    split.append(codon)
for word in split:
    vocabulary[word]=vocabulary.get(word,0)+1
#print("vocabulary: ",vocabulary)
print("vocabulary length: ",len(vocabulary))
