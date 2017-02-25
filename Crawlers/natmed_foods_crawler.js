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

/// SCIENTIFIC NAMES --------------------------
    self.scientficNames = [];

    var el = $("#scientificName-content");

    // Gets the family name of the element
    if (el.text().match(/Family:(.*)/).length > 0) {
        self.familyName = el.text().match(/Family:(.*)/)[0]
                                   .split(":")[1].trim()
                                   .replace(".", "");
    }

    // Get the scientific names
    $(el.children()).each(function (k, v) {
        if (v.tagName == 'NDB:NAME') {
            self.scientficNames.push($(v).text());
        }
    });

/// -------------------------------------------

}

console.log(JSON.stringify(new Food(), null, '\t'));