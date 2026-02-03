/* utf-8 */
document.addEventListener("DOMContentLoaded", function () {
// 获取包含随机文章的<ul>元素
    var randomArticles = document.getElementById("random-articles");

// 引入文章数据
    var script = document.createElement("script");
    script.src = "articles.js";
    script.onload = function () {
// 随机打乱文章数据的顺序
        var shuffledArticles = shuffle(articlesData);

// 选择前10个随机文章
        var selectedArticles = shuffledArticles.slice(0, 10);

// 创建并插入<li>元素，展示随机文章
        selectedArticles.forEach(function (article) {
            var li = document.createElement("li");
            var a = document.createElement("a");
            a.href = article.url;
            a.textContent = article.title;
            li.appendChild(a);
            randomArticles.appendChild(li);
        });
    };
    document.head.appendChild(script);

// Fisher-Yates洗牌算法，用于打乱数组顺序
    function shuffle(array) {
        var currentIndex = array.length;
        var temporaryValue, randomIndex;

        while (0 !== currentIndex) {
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex -= 1;

            temporaryValue = array[currentIndex];
            array[currentIndex] = array[randomIndex];
            array[randomIndex] = temporaryValue;
        }

        return array;
    }
});