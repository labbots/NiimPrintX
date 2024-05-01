class CanvasOperation:
    def __init__(self, config, text_op, img_op):
        self.config = config
        self.text_op = text_op
        self.img_op = img_op

    def canvas_click_handler(self, event):
        """Deselect text if clicking outside the bounding box or on the resize handle."""
        if self.config.current_selected:
            text_bbox = self.config.text_items[self.config.current_selected]["bbox"]
            x1, y1, x2, y2 = self.config.canvas.coords(text_bbox)
            text_bbox_handler = self.config.text_items[self.config.current_selected]["handle"]
            hx1, hy1, hx2, hy2 = self.config.canvas.coords(text_bbox_handler)

            # Check if the click is on the handler
            if hx1 <= event.x <= hx2 and hy1 <= event.y <= hy2:
                return

            # Check if the click is inside the bounding box
            if not (x1 <= event.x <= x2 and y1 <= event.y <= y2):
                self.text_op.deselect_text()

        if self.config.current_selected_image:
            img_bbox = self.config.image_items[self.config.current_selected_image]["bbox"]
            x1, y1, x2, y2 = self.config.canvas.coords(img_bbox)
            img_bbox_handler = self.config.image_items[self.config.current_selected_image]["handle"]
            hx1, hy1, hx2, hy2 = self.config.canvas.coords(img_bbox_handler)

            # Check if the click is on the handler
            if hx1 <= event.x <= hx2 and hy1 <= event.y <= hy2:
                return

            # Check if the click is inside the bounding box
            if not (x1 <= event.x <= x2 and y1 <= event.y <= y2):
                self.img_op.deselect_image()