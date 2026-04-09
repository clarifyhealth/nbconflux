from nbconvert.filters.markdown_mistune import IPythonRenderer


class ConfluenceMarkdownRenderer(IPythonRenderer):
    def image(self, alt_text, url='', title=None):
        """Renders a Markdown image as a Confluence image tag.

        Parameters
        ----------
        alt_text: str
            Alternative text description of the image
        url: str
            Image source URL
        title: str
            Image title attribute

        Returns
        -------
        str
            Confluence storage format image tag
        """
        title_attr = 'ac:title="{}"'.format(title) if title else ''
        alt_attr = 'ac:alt="{}"'.format(alt_text) if alt_text else ''
        html = (
            '<ac:image {title} {alt}><ri:url ri:value="{src}" /></ac:image>'
            .format(title=title_attr, alt=alt_attr, src=url)
        )
        return html
