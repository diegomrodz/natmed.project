var arr = [];

$(".reference-detail").each(function (k, el) {
    var obj = {};
    
    obj.id = $(el).find(".reference-number-column").text().trim();
    
    obj.text = $(el).find(".reference-text-column")
                    .text().trim()
                    .split("\n")[0].trim();

    obj.link = $(el).find(".reference-text-column a").attr("href");

    arr.push(obj);
});

console.log(JSON.stringify(arr, null, "\t"));
//return arr;