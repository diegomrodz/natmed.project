function download(filename, content) {
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(content));
    pom.setAttribute('download', filename);

    pom.click();
}

function Food() {
    var self = this;

    self.name = $("h1").text();
    self.image_url = $("#Pic img")[0].src;

    self.references = [];

/// SCIENTIFIC NAMES -----------------------------------------------------------
    self.scientficNames = [];

    var el = $("#scientificName-content");

    if (el.text().match(/Family:(.*)/).length > 0) {
        self.familyName = el.text().match(/Family:(.*)/)[0]
                                   .split(":")[1].trim()
                                   .replace(".", "");
    }

    $(el.children()).each(function (k, v) {
        if (v.tagName == 'NDB:NAME') {
            self.scientficNames.push($(v).text());
        }
    });

/// BACKGROUND -----------------------------------------------------------------    
    var el = document.querySelector("#background-content");

    if (el) {
        self.description = el.textContent.trim().replace(/\([0-9|, ]+\)/gi, '');

        $("#background-content a").each(function (k, v) {
            self.references.push(v.href);
        });
    }

/// ALSO KNOW AS ---------------------------------------------------------------
    self.alsoKnowAs = [];

    var el = document.querySelector("#alsoKnownAs-content");

    if (el) {
        $(el.children).each(function (k, v) {
            if (v.tagName == 'NDB:NAME') {
                self.alsoKnowAs.push(v.textContent);
            }
        });
    }

/// HISTORY --------------------------------------------------------------------
    var el = document.querySelector("#history-content");

    if (el) {
        self.history = el.textContent.trim().replace(/\([0-9|, ]+\)/gi, '');

        $("#history-content a").each(function (k, v) {
            self.references.push(v.href);
        });
    }

/// PEOPLE USE THIS FOR --------------------------------------------------------
    var el = document.querySelector("#peopleUseThisFor-content");

    if (el) {
        self.peopleUseThisFor = el.textContent.trim().replace(/\([0-9|, ]+\)/gi, '');

        $("#peopleUseThisFor-content a").each(function (k, v) {
            self.references.push(v.href);
        });
    }

/// SAFETY ---------------------------------------------------------------------
    self.safetyInfo = [];

    var el = document.querySelector("#safety-content");

    if (el) {
        $(el.innerHTML.split("<br><br>")).each(function (k, e) {
            try {
                var html = $(e);
                var obj = {};

                obj.safety = html.children("a strong")[0].textContent;

                obj.text = html.text().trim()
                               .replace(obj.safety, "")
                               .replace(/\([0-9|, ]+\)/gi, '');

                var parts = obj.text.split(/:/);

                if (parts.length > 1) {
                    obj.context = parts[0];
                    obj.text = obj.text.replace(parts[0] + ":", "").trim();
                }

                obj.references = [];

                html.siblings("a").each(function (k2, a) {
                    if (k2 == 0) {
                        obj.url = a.href;
                    } else {
                        obj.references.push(a.href);
                    }
                });

                self.safetyInfo.push(obj);
            } catch (ex) {
                console.log('Erro at', k);
            }
        });
    }

/// EFECTIVENESS ---------------------------------------------------------------
    self.effectivenessInfo = [];

    var el = document.querySelector("#effectiveness-content");

    var lastEffectiveness = "";

    if (el) {
        $(el.innerHTML.split("<br><br>")).each(function (k, v) {
            try {
                var html = $(v);
                var obj = {};

                var headers = html.children("a strong");

                if (headers.length >= 2) {
                    lastEffectiveness = headers[0].textContent;
                    obj.disease = headers[1].textContent;
                } else {
                    obj.disease = headers[0].textContent;
                }

                obj.effectiveness = lastEffectiveness;

                obj.text = html.text().trim()
                               .replace(obj.disease, "")
                               .replace(obj.effectiveness, "")
                               .replace(/\([0-9|, ]+\)/gi, '');

                self.effectivenessInfo.push(obj);

                obj.references = [];

                html.siblings("a").each(function (k2, a) {
                    if (headers.length >= 2) {
                        if (k2 == 1) {
                            obj.url = a.href;
                        } else if (k2 > 1) {
                            obj.references.push(a.href);
                        }
                    } else {
                        if (k2 == 0) {
                            obj.url = a.href;
                        } else {
                            obj.references.push(a.href);
                        }
                    }
                });

                self.safetyInfo.push(obj);
            } catch (ex) {

            }
        });
    }

/// Dosing and Adminstration
    var el = document.querySelector("#dosing-content");

    self.dosingInfo = [];

    if (el) {
        $(el).children("ul").each(function (k, ul) {
            $(ul).children("li").each(function (k, li) {
                var title = $(li).children("h3").text();
                var content = $(li).children(".section-content")[0];

                $(content.innerHTML.split("<br><br>")).each(function (k, section) {
                    try {
                        var html = $(section);
                        var obj = {};

                        if (title && title != "") {
                            obj.for = title;
                        }

                        obj.references = [];

                        if (obj.for == "Standardization & Formulation") {
                            obj.text = $(content).text();
                            
                            $(content).children("a").each(function (k, a) {
                                obj.references.push(a.href);
                            });
                        } else {
                            obj.disease = html.siblings("strong").text();
                            
                            obj.text = html.text().split(":").pop()
                                       .replace(/\([0-9|, ]+\)/gi, '')
                                       .trim();
                            
                            html.siblings("a").each(function (k, a) {
                                obj.references.push(a.href);
                            });
                        }

                        if (obj.text != "") {
                            self.dosingInfo.push(obj);
                        }
                    } catch (e) {
                    }
                });
            });
        });
    }

/// Adverse Effects
    var el = document.querySelector("#adverseEvents-content");

    self.adverseEffects = {
        text: [],
        domains: []
    };

    if (el) {
        $(el).children(".section-content").each(function (k, section) {
            var obj = {};
            
            obj.title = $(section).children("strong")
                                  .text()
                                  .replace(":", "");

            obj.text = section.textContent
                       .split(":").pop()
                       .replace(/\([0-9|, ]+\)/gi, '')
                       .trim();
            
            obj.references = [];

            $(section).children("a").each(function (k, a) {
                obj.references.push(a.href);
            });

            self.adverseEffects.text.push(obj);
        });

        $(el).children("ul").each(function (k, ul) {
            var obj = {};
            var content = $(ul).children("li")[0];

            obj.title = $(content)
                          .children("h3")
                          .text()
                          .trim();
            
            obj.text =  $(content).children(".section-content")
                            .text()
                            .replace(/\([0-9|, ]+\)/gi, '')                            
                            .trim();
            
            obj.references = [];

            $(content).children(".section-content").children("a").each(function (k, a) {
                obj.references.push(a.href);
            });

            self.adverseEffects.domains.push(obj);
        });
    }
}

console.log(JSON.stringify(new Food(), null, '\t'));