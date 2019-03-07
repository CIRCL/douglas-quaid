pandoc -S -s -f latex -t markdown_github --toc --toc-depth=2 --filter=pandoc-citeproc --bibliography=./../Working_Directory_Random/StateOfTheArt/carl-hauser.bib --csl=./../Working_Directory_Random/StateOfTheArt/acm-sigchi-proceedings.csl -o ./../Working_Directory_Random/StateOfTheArt/SOTA.md ./../Working_Directory_Random/StateOfTheArt/SOTA.tex

cp ./../Working_Directory_Random/StateOfTheArt/SOTA.md ./../carl-hauser/SOTA/SOTA.md
cp ./../Working_Directory_Random/StateOfTheArt/SOTA.pdf ./../carl-hauser/SOTA/SOTA.pdf
cp -r ./../Working_Directory_Random/StateOfTheArt/sota-ressources/* ./SOTA/sota-ressources/

git add ./SOTA/SOTA.*
git add ./SOTA/sota-ressources/*
git commit -m "add: [SOTA] updates"
git push