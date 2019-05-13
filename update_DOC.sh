pandoc -S -s -f latex -t markdown_github --toc --toc-depth=2 --filter=pandoc-citeproc --bibliography=./../Working_Directory_Random/StateOfTheArt/carl-hauser.bib --csl=./../Working_Directory_Random/StateOfTheArt/acm-sigchi-proceedings.csl -o ./../Working_Directory_Random/StateOfTheArt/Carlhauser_core_doc.md ./../Working_Directory_Random/StateOfTheArt/Carlhauser_core_doc.tex

cp ./../Working_Directory_Random/StateOfTheArt/Carlhauser_core_doc.md ./../carl-hauser/SOTA/Core_doc.md
cp ./../Working_Directory_Random/StateOfTheArt/Carlhauser_core_doc.pdf ./../carl-hauser/SOTA/Core_doc.pdf
cp -r ./../Working_Directory_Random/StateOfTheArt/carlhauser-doc/* ./SOTA/carlhauser-doc/

git add ./SOTA/Core_doc.*
git add ./SOTA/carlhauser-doc/*
git commit -m "add: [DOC] updates"
git push