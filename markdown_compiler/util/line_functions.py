'''
Each of the functions in this file takes a single line of input and transforms the line in some way.
'''


def _inside_inline_code(line, index):
    '''
    Return True if position `index` sits inside a `backtick` span.
    Markdown markers inside inline code should be left alone.

    >>> _inside_inline_code('a `*b*` c', 3)
    True
    >>> _inside_inline_code('a `*b*` c', 0)
    False
    '''
    return line[:index].count('`') % 2 == 1 and '`' in line[index:]


def _compile_delimited(line, delimiter, tag, skip_code=True, escape=False):
    '''
    Replace every `delimiter`text`delimiter` pair in line with <tag>text</tag>.
    Unmatched delimiters and empty pairs are left unchanged.
    If escape is True, < and > inside the pair become &lt; and &gt;.

    >>> _compile_delimited('a *b* c *d', '*', 'i')
    'a <i>b</i> c *d'
    >>> _compile_delimited('```', '`', 'code', skip_code=False)
    '```'
    '''
    size = len(delimiter)
    result = ''
    pos = 0
    while True:
        start = line.find(delimiter, pos)
        while skip_code and start != -1 and _inside_inline_code(line, start):
            start = line.find(delimiter, start + 1)
        if start == -1:
            break
        end = line.find(delimiter, start + size)
        while skip_code and end != -1 and _inside_inline_code(line, end):
            end = line.find(delimiter, end + 1)
        if end == -1:
            break
        content = line[start + size:end]
        if content == '':
            # an empty pair like `` is not markup; keep one character and move on
            result += line[pos:start + 1]
            pos = start + 1
            continue
        if escape:
            content = content.replace('<', '&lt;').replace('>', '&gt;')
        result += line[pos:start] + '<' + tag + '>' + content + '</' + tag + '>'
        pos = end + size
    return result + line[pos:]


def _compile_bracketed(line, prefix, make_tag):
    '''
    Find `prefix[text](url)` patterns and replace them with make_tag(text, url).
    Used by both links (prefix '[') and images (prefix '![').
    '''
    result = ''
    pos = 0
    while True:
        start = line.find(prefix, pos)
        if start == -1:
            break
        # a link should not swallow the "[" of an image
        if prefix == '[' and start > 0 and line[start - 1] == '!':
            result += line[pos:start + 1]
            pos = start + 1
            continue
        middle = line.find('](', start + len(prefix))
        if middle == -1:
            break
        end = line.find(')', middle + 2)
        if end == -1:
            break
        text = line[start + len(prefix):middle]
        url = line[middle + 2:end]
        result += line[pos:start] + make_tag(text, url)
        pos = end + 1
    return result + line[pos:]


def compile_headers(line):
    '''
    Convert markdown headers into <h1>,<h2>,etc tags.

    HINT:
    This is the simplest function to implement in this assignment.
    Use a slices to extract the first part of the line,
    then use if statements to check if they match the appropriate header markdown commands.

    >>> compile_headers('# This is the main header')
    '<h1> This is the main header</h1>'
    >>> compile_headers('## This is a sub-header')
    '<h2> This is a sub-header</h2>'
    >>> compile_headers('### This is a sub-header')
    '<h3> This is a sub-header</h3>'
    >>> compile_headers('#### This is a sub-header')
    '<h4> This is a sub-header</h4>'
    >>> compile_headers('##### This is a sub-header')
    '<h5> This is a sub-header</h5>'
    >>> compile_headers('###### This is a sub-header')
    '<h6> This is a sub-header</h6>'
    >>> compile_headers('      # this is not a header')
    '      # this is not a header'
    '''
    hashes = 0
    while hashes < len(line) and line[hashes] == '#':
        hashes += 1
    if 1 <= hashes <= 6 and line[hashes:hashes + 1] == ' ':
        return '<h' + str(hashes) + '>' + line[hashes:] + '</h' + str(hashes) + '>'
    return line


def compile_italic_star(line):
    '''
    Convert "*italic*" into "<i>italic</i>".

    HINT:
    Italics require carefully tracking the beginning and ending positions of the text to be replaced.
    Use the find and slice operations from the Strings and Files reading.
    Find the opening marker, then search for its closing partner after it.
    Keep unmatched markers unchanged, as the doctests show.

    >>> compile_italic_star('*This is italic!* This is not italic.')
    '<i>This is italic!</i> This is not italic.'
    >>> compile_italic_star('*This is italic!*')
    '<i>This is italic!</i>'
    >>> compile_italic_star('This is *italic*!')
    'This is <i>italic</i>!'
    >>> compile_italic_star('This is not *italic!')
    'This is not *italic!'
    >>> compile_italic_star('*')
    '*'
    '''
    return _compile_delimited(line, '*', 'i')


def compile_italic_underscore(line):
    '''
    Convert "_italic_" into "<i>italic</i>".

    HINT:
    This function is almost exactly the same as `compile_italic_star`.

    >>> compile_italic_underscore('_This is italic!_ This is not italic.')
    '<i>This is italic!</i> This is not italic.'
    >>> compile_italic_underscore('_This is italic!_')
    '<i>This is italic!</i>'
    >>> compile_italic_underscore('This is _italic_!')
    'This is <i>italic</i>!'
    >>> compile_italic_underscore('This is not _italic!')
    'This is not _italic!'
    >>> compile_italic_underscore('_')
    '_'
    '''
    return _compile_delimited(line, '_', 'i')


def compile_strikethrough(line):
    '''
    Convert "~~strikethrough~~" to "<ins>strikethrough</ins>".

    HINT:
    The strikethrough annotations are very similar to implement as the italic function.
    The difference is that there are two delimiting characters instead of one.
    This will require carefully thinking about the range of your for loop and all of your list indexing.

    >>> compile_strikethrough('~~This is strikethrough!~~ This is not strikethrough.')
    '<ins>This is strikethrough!</ins> This is not strikethrough.'
    >>> compile_strikethrough('~~This is strikethrough!~~')
    '<ins>This is strikethrough!</ins>'
    >>> compile_strikethrough('This is ~~strikethrough~~!')
    'This is <ins>strikethrough</ins>!'
    >>> compile_strikethrough('This is not ~~strikethrough!')
    'This is not ~~strikethrough!'
    >>> compile_strikethrough('~~')
    '~~'
    '''
    return _compile_delimited(line, '~~', 'ins')


def compile_bold_stars(line):
    '''
    Convert "**bold**" to "<b>bold</b>".

    HINT:
    This function is similar to the strikethrough function.

    >>> compile_bold_stars('**This is bold!** This is not bold.')
    '<b>This is bold!</b> This is not bold.'
    >>> compile_bold_stars('**This is bold!**')
    '<b>This is bold!</b>'
    >>> compile_bold_stars('This is **bold**!')
    'This is <b>bold</b>!'
    >>> compile_bold_stars('This is not **bold!')
    'This is not **bold!'
    >>> compile_bold_stars('**')
    '**'
    '''
    return _compile_delimited(line, '**', 'b')


def compile_bold_underscore(line):
    '''
    Convert "__bold__" to "<b>bold</b>".

    HINT:
    This function is similar to the strikethrough function.

    >>> compile_bold_underscore('__This is bold!__ This is not bold.')
    '<b>This is bold!</b> This is not bold.'
    >>> compile_bold_underscore('__This is bold!__')
    '<b>This is bold!</b>'
    >>> compile_bold_underscore('This is __bold__!')
    'This is <b>bold</b>!'
    >>> compile_bold_underscore('This is not __bold!')
    'This is not __bold!'
    >>> compile_bold_underscore('__')
    '__'
    '''
    return _compile_delimited(line, '__', 'b')


def compile_code_inline(line):
    '''
    Add <code> tags.

    HINT:
    This function is like the italics functions because inline code uses only a single character as a delimiter.
    It is more complex, however, because inline code blocks can contain valid HTML inside of them,
    but we do not want that HTML to get rendered as HTML.
    Therefore, we must convert the `<` and `>` signs into `&lt;` and `&gt;` respectively.

    >>> compile_code_inline('You can use backticks like this (`1+2`) to include code in the middle of text.')
    'You can use backticks like this (<code>1+2</code>) to include code in the middle of text.'
    >>> compile_code_inline('This is inline code: `1+2`')
    'This is inline code: <code>1+2</code>'
    >>> compile_code_inline('`1+2`')
    '<code>1+2</code>'
    >>> compile_code_inline('This example has html within the code: `<b>bold!</b>`')
    'This example has html within the code: <code>&lt;b&gt;bold!&lt;/b&gt;</code>'
    >>> compile_code_inline('this example has a math formula in the  code: `1 + 2 < 4`')
    'this example has a math formula in the  code: <code>1 + 2 &lt; 4</code>'
    >>> compile_code_inline('this example has a <b>math formula</b> in the  code: `1 + 2 < 4`')
    'this example has a <b>math formula</b> in the  code: <code>1 + 2 &lt; 4</code>'
    >>> compile_code_inline('```')
    '```'
    >>> compile_code_inline('```python3')
    '```python3'
    '''
    return _compile_delimited(line, '`', 'code', skip_code=False, escape=True)


def compile_links(line):
    '''
    Add <a> tags.

    HINT:
    The links and images are potentially more complicated because they have many types of delimeters: `[]()`.
    These delimiters are not symmetric, however, so we can more easily find the start and stop locations using the strings find function.

    >>> compile_links('Click on the [course webpage](https://github.com/mikeizbicki/cmc-csci040)!')
    'Click on the <a href="https://github.com/mikeizbicki/cmc-csci040">course webpage</a>!'
    >>> compile_links('[course webpage](https://github.com/mikeizbicki/cmc-csci040)')
    '<a href="https://github.com/mikeizbicki/cmc-csci040">course webpage</a>'
    >>> compile_links('this is wrong: [course webpage]    (https://github.com/mikeizbicki/cmc-csci040)')
    'this is wrong: [course webpage]    (https://github.com/mikeizbicki/cmc-csci040)'
    >>> compile_links('this is wrong: [course webpage](https://github.com/mikeizbicki/cmc-csci040')
    'this is wrong: [course webpage](https://github.com/mikeizbicki/cmc-csci040'
    '''
    return _compile_bracketed(
        line, '[', lambda text, url: '<a href="' + url + '">' + text + '</a>')


def compile_images(line):
    '''
    Add <img> tags.

    HINT:
    Images are formatted in markdown almost exactly the same as links,
    except that images have a leading `!`.
    So your code here should be based off of the <a> tag code.

    >>> compile_images('[Mike Izbicki](https://avatars1.githubusercontent.com/u/1052630?v=2&s=460)')
    '[Mike Izbicki](https://avatars1.githubusercontent.com/u/1052630?v=2&s=460)'
    >>> compile_images('![Mike Izbicki](https://avatars1.githubusercontent.com/u/1052630?v=2&s=460)')
    '<img src="https://avatars1.githubusercontent.com/u/1052630?v=2&s=460" alt="Mike Izbicki" />'
    >>> compile_images('This is an image of Mike Izbicki: ![Mike Izbicki](https://avatars1.githubusercontent.com/u/1052630?v=2&s=460)')
    'This is an image of Mike Izbicki: <img src="https://avatars1.githubusercontent.com/u/1052630?v=2&s=460" alt="Mike Izbicki" />'
    '''
    return _compile_bracketed(
        line, '![', lambda text, url: '<img src="' + url + '" alt="' + text + '" />')
