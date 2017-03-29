
function PubmedArticle () {
    var self = this;
    
    try {
        self.title = document.querySelector("#maincontent h1").textContent;
        self.authors = [];
        self.organizations = [];

        var authors = document.querySelectorAll("#maincontent .auths a");

        if (authors) {
            authors.forEach(function (e) {
                self.authors.push(e.textContent);
            });
        }

        var orgs = document.querySelectorAll("#maincontent .afflist dd");

        if (orgs) {
            orgs.forEach(function (e) {
                self.organizations.push(e.textContent);
            });
        }

        var text = document.querySelector("#maincontent abstracttext");

        if (text) {
            self.text = text.textContent;
            self.has_abstract = true;
        } else {
            self.has_abstract = false;
        }
    } catch (e) {
    }

}

return JSON.stringify(new PubmedArticle(), null, "\t");