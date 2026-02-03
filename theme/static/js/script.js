/* utf-8 */

$(document).ready(function () {
    // 代码高亮
    $('div.highlight').each(function () {
        hljs.highlightBlock(this);

        // 创建按钮元素
        const button = $('<button class="hljs-copy-button" data-copied="false">Copy</button>');

        // 将按钮插入到 div.highlight 元素中
        $(this).append(button);
    });
    // 复制到剪贴板
    $('.hljs-copy-button').click(function () {
        // 获取父级元素中的文本
        var text = $(this).parent('.highlight').find('code').text();
        // 创建一个临时的textarea元素
        var $textarea = $('<textarea>').val(text).appendTo('body').select();
        // 复制文本到剪贴板
        document.execCommand('copy');
        // 删除临时元素
        $textarea.remove();
        // 改变按钮的文本
        $(this).text('Copied!');
    });

    // TAG标签实现
    // 获取 URL 参数值
    function getParameterByName(name, url) {
        name = name.replace(/[\[\]]/g, '\\$&');
        var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)', 'i'),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, ' '));
    }

    // 使用 jQuery 获取 tag 参数的值
    var tag = getParameterByName('tag', window.location.href);

    if (tag) {
        // 隐藏所有的 <li> 元素
        $('.all-post ul li').hide();
        $('.all-post .box h2').hide();

        // 显示包含指定 tag 的 <li> 元素（忽略大小写）
        $('.all-post ul li').each(function () {
            var liText = $(this).text().toLowerCase();
            if (liText.indexOf(tag.toLowerCase()) !== -1) {
                $(this).show();
                $(this).closest('.box').find('h2').show();
            }
        });
    }
});