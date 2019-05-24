pandoc -S -s -f latex -t markdown_github --toc --toc-depth=2 --filter=pandoc-citeproc --bibliography=./../Working_Directory_Random/StateOfTheArt/carl-hauser.bib --csl=./../Working_Directory_Random/StateOfTheArt/acm-sigchi-proceedings.csl -o ./../Working_Directory_Random/StateOfTheArt/Carlhauser_core_doc.md ./../Working_Directory_Random/StateOfTheArt/Carlhauser_core_doc.tex

# cp ./../Working_Directory_Random/StateOfTheArt/Carlhauser_core_doc.md ./../douglas-quaid/docs/code_doc/core_doc.md
cp ./../Working_Directory_Random/StateOfTheArt/Carlhauser_core_doc.pdf ./../douglas-quaid/docs/code_doc/core_doc.pdf
cp -r ./../Working_Directory_Random/StateOfTheArt/carlhauser-doc/* ./docs/code_doc/ressources/

git add ./docs/code_doc/code_doc.*
git commit -m "auto: [DOC] updates"
git push