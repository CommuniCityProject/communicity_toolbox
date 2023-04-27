import os
from pathlib import Path
from typing import List

import cv2
import numpy as np
import tensorflow as tf

from toolbox.Structures import BoundingBox, Instance

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class FaceDetector:

    def __init__(self, model_path: Path, use_cuda: bool = False):
        """Face detector

        Args:
            model_path (Path): _description_
            use_cuda (bool, optional): _description_. Defaults to False.
        """
        if not use_cuda:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        with tf.Graph().as_default() as full_graph:
            tf.import_graph_def(self._load_graph_def(model_path), name="")
        self._session = tf.compat.v1.Session(graph=full_graph)
        self._pnet, self._rnet, self._onet = self._load_mtcnn(full_graph)

    def _load_graph_def(self, model_path: Path):
        graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(model_path, "rb") as f:
            graph_def.ParseFromString(f.read())
        return graph_def

    def _load_mtcnn(self, graph):
        pnet_out_1 = graph.get_tensor_by_name('pnet/conv4-2/BiasAdd:0')
        pnet_out_2 = graph.get_tensor_by_name('pnet/prob1:0')
        pnet_in = graph.get_tensor_by_name('pnet/input:0')

        rnet_out_1 = graph.get_tensor_by_name('rnet/conv5-2/conv5-2:0')
        rnet_out_2 = graph.get_tensor_by_name('rnet/prob1:0')
        rnet_in = graph.get_tensor_by_name('rnet/input:0')

        onet_out_1 = graph.get_tensor_by_name('onet/conv6-2/conv6-2:0')
        onet_out_2 = graph.get_tensor_by_name('onet/conv6-3/conv6-3:0')
        onet_out_3 = graph.get_tensor_by_name('onet/prob1:0')
        onet_in = graph.get_tensor_by_name('onet/input:0')

        def pnet_fun(img): return self._session.run(
            (pnet_out_1, pnet_out_2), feed_dict={pnet_in: img}
        )

        def rnet_fun(img): return self._session.run(
            (rnet_out_1, rnet_out_2), feed_dict={rnet_in: img}
        )

        def onet_fun(img): return self._session.run(
            (onet_out_1, onet_out_2, onet_out_3), feed_dict={onet_in: img}
        )
        return pnet_fun, rnet_fun, onet_fun

    def _bbreg(self, boundingbox, reg):
        if reg.shape[1] == 1:
            reg = np.reshape(reg, (reg.shape[2], reg.shape[3]))

        w = boundingbox[:, 2]-boundingbox[:, 0]+1
        h = boundingbox[:, 3]-boundingbox[:, 1]+1
        b1 = boundingbox[:, 0]+reg[:, 0]*w
        b2 = boundingbox[:, 1]+reg[:, 1]*h
        b3 = boundingbox[:, 2]+reg[:, 2]*w
        b4 = boundingbox[:, 3]+reg[:, 3]*h
        boundingbox[:, 0:4] = np.transpose(np.vstack([b1, b2, b3, b4]))
        return boundingbox

    def _generateBoundingBox(self, imap, reg, scale, t):
        stride = 2
        cellsize = 12

        imap = np.transpose(imap)
        dx1 = np.transpose(reg[:, :, 0])
        dy1 = np.transpose(reg[:, :, 1])
        dx2 = np.transpose(reg[:, :, 2])
        dy2 = np.transpose(reg[:, :, 3])
        y, x = np.where(imap >= t)
        if y.shape[0] == 1:
            dx1 = np.flipud(dx1)
            dy1 = np.flipud(dy1)
            dx2 = np.flipud(dx2)
            dy2 = np.flipud(dy2)
        score = imap[(y, x)]
        reg = np.transpose(
            np.vstack([dx1[(y, x)], dy1[(y, x)], dx2[(y, x)], dy2[(y, x)]])
        )
        if reg.size == 0:
            reg = np.empty((0, 3))
        bb = np.transpose(np.vstack([y, x]))
        q1 = np.fix((stride*bb+1)/scale)
        q2 = np.fix((stride*bb+cellsize-1+1)/scale)
        boundingbox = np.hstack([q1, q2, np.expand_dims(score, 1), reg])
        return boundingbox, reg

    def _nms(self, boxes, threshold, method):
        if boxes.size == 0:
            return np.empty((0, 3))
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        s = boxes[:, 4]
        area = (x2-x1+1) * (y2-y1+1)
        I = np.argsort(s)
        pick = np.zeros_like(s, dtype=np.int16)
        counter = 0
        while I.size > 0:
            i = I[-1]
            pick[counter] = i
            counter += 1
            idx = I[0:-1]
            xx1 = np.maximum(x1[i], x1[idx])
            yy1 = np.maximum(y1[i], y1[idx])
            xx2 = np.minimum(x2[i], x2[idx])
            yy2 = np.minimum(y2[i], y2[idx])
            w = np.maximum(0.0, xx2-xx1+1)
            h = np.maximum(0.0, yy2-yy1+1)
            inter = w * h
            if method == 'Min':
                o = inter / np.minimum(area[i], area[idx])
            else:
                o = inter / (area[i] + area[idx] - inter)
            I = I[np.where(o <= threshold)]
        pick = pick[0:counter]
        return pick

    def _pad(self, total_boxes, w, h):
        tmpw = (total_boxes[:, 2]-total_boxes[:, 0]+1).astype(np.int32)
        tmph = (total_boxes[:, 3]-total_boxes[:, 1]+1).astype(np.int32)
        numbox = total_boxes.shape[0]

        dx = np.ones((numbox), dtype=np.int32)
        dy = np.ones((numbox), dtype=np.int32)
        edx = tmpw.copy().astype(np.int32)
        edy = tmph.copy().astype(np.int32)

        x = total_boxes[:, 0].copy().astype(np.int32)
        y = total_boxes[:, 1].copy().astype(np.int32)
        ex = total_boxes[:, 2].copy().astype(np.int32)
        ey = total_boxes[:, 3].copy().astype(np.int32)

        tmp = np.where(ex > w)
        edx.flat[tmp] = np.expand_dims(-ex[tmp]+w+tmpw[tmp], 1)
        ex[tmp] = w

        tmp = np.where(ey > h)
        edy.flat[tmp] = np.expand_dims(-ey[tmp]+h+tmph[tmp], 1)
        ey[tmp] = h

        tmp = np.where(x < 1)
        dx.flat[tmp] = np.expand_dims(2-x[tmp], 1)
        x[tmp] = 1

        tmp = np.where(y < 1)
        dy.flat[tmp] = np.expand_dims(2-y[tmp], 1)
        y[tmp] = 1

        return dy, edy, dx, edx, y, ey, x, ex, tmpw, tmph

    def _rerec(self, bboxA):
        h = bboxA[:, 3] - bboxA[:, 1]
        w = bboxA[:, 2] - bboxA[:, 0]
        l = np.maximum(w, h)
        bboxA[:, 0] = bboxA[:, 0]+w*0.5-l*0.5
        bboxA[:, 1] = bboxA[:, 1]+h*0.5-l*0.5
        bboxA[:, 2:4] = bboxA[:, 0:2] + np.transpose(np.tile(l, (2, 1)))
        return bboxA

    def predict(self, img: np.ndarray) -> List[Instance]:
        threshold = [0.6, 0.7, 0.9]
        factor = 0.709
        factor_count = 0
        total_boxes = np.empty((0, 9))
        points = np.array([])
        h = img.shape[0]
        w = img.shape[1]
        minl = np.amin([h, w])
        m = 12.0/32
        minl = minl*m
        scales = []
        while minl >= 12:
            scales += [m*np.power(factor, factor_count)]
            minl = minl*factor
            factor_count += 1

        for j in range(len(scales)):
            scale = scales[j]
            hs = int(np.ceil(h*scale))
            ws = int(np.ceil(w*scale))
            im_data = cv2.resize(img, (ws, hs), interpolation=cv2.INTER_AREA)
            im_data = (im_data-127.5)*0.0078125
            img_x = np.expand_dims(im_data, 0)
            img_y = np.transpose(img_x, (0, 2, 1, 3))
            out = self._pnet(img_y)
            out0 = np.transpose(out[0], (0, 2, 1, 3))
            out1 = np.transpose(out[1], (0, 2, 1, 3))

            boxes, _ = self._generateBoundingBox(
                out1[0, :, :, 1].copy(),
                out0[0, :, :, :].copy(),
                scale,
                threshold[0]
            )

            pick = self._nms(boxes.copy(), 0.5, 'Union')
            if boxes.size > 0 and pick.size > 0:
                boxes = boxes[pick, :]
                total_boxes = np.append(total_boxes, boxes, axis=0)
        numbox = total_boxes.shape[0]
        if numbox > 0:
            pick = self._nms(total_boxes.copy(), 0.7, 'Union')
            total_boxes = total_boxes[pick, :]
            regw = total_boxes[:, 2]-total_boxes[:, 0]
            regh = total_boxes[:, 3]-total_boxes[:, 1]
            qq1 = total_boxes[:, 0]+total_boxes[:, 5]*regw
            qq2 = total_boxes[:, 1]+total_boxes[:, 6]*regh
            qq3 = total_boxes[:, 2]+total_boxes[:, 7]*regw
            qq4 = total_boxes[:, 3]+total_boxes[:, 8]*regh
            total_boxes = np.transpose(
                np.vstack([qq1, qq2, qq3, qq4, total_boxes[:, 4]]))
            total_boxes = self._rerec(total_boxes.copy())
            total_boxes[:, 0:4] = np.fix(total_boxes[:, 0:4]).astype(np.int32)
            dy, edy, dx, edx, y, ey, x, ex, tmpw, tmph = self._pad(
                total_boxes.copy(), w, h)
        else:
            return []

        numbox = total_boxes.shape[0]
        if numbox > 0:
            tempimg = np.zeros((24, 24, 3, numbox))
            for k in range(0, numbox):
                tmp = np.zeros((int(tmph[k]), int(tmpw[k]), 3))
                tmp[dy[k]-1:edy[k], dx[k]-1:edx[k], :] = \
                    img[y[k]-1:ey[k], x[k]-1:ex[k], :]
                if tmp.shape[0] > 0 and tmp.shape[1] > 0 or \
                        tmp.shape[0] == 0 and tmp.shape[1] == 0:
                    tempimg[:, :, :, k] = cv2.resize(
                        tmp, (24, 24), interpolation=cv2.INTER_AREA)
                else:
                    return np.empty()
            tempimg = (tempimg-127.5)*0.0078125
            tempimg1 = np.transpose(tempimg, (3, 1, 0, 2))
            out = self._rnet(tempimg1)
            out0 = np.transpose(out[0])
            out1 = np.transpose(out[1])
            score = out1[1, :]
            ipass = np.where(score > threshold[1])
            total_boxes = np.hstack(
                [total_boxes[ipass[0], 0:4].copy(),
                 np.expand_dims(score[ipass].copy(), 1)]
            )
            mv = out0[:, ipass[0]]
            if total_boxes.shape[0] > 0:
                pick = self._nms(total_boxes, 0.7, 'Union')
                total_boxes = total_boxes[pick, :]
                total_boxes = self._bbreg(
                    total_boxes.copy(),
                    np.transpose(mv[:, pick])
                )
                total_boxes = self._rerec(total_boxes.copy())
        else:
            return []

        numbox = total_boxes.shape[0]
        if numbox > 0:
            total_boxes = np.fix(total_boxes).astype(np.int32)
            dy, edy, dx, edx, y, ey, x, ex, tmpw, tmph = self._pad(
                total_boxes.copy(), w, h)
            tempimg = np.zeros((48, 48, 3, numbox))
            for k in range(0, numbox):
                tmp = np.zeros((int(tmph[k]), int(tmpw[k]), 3))
                tmp[dy[k]-1:edy[k], dx[k]-1:edx[k], :] = \
                    img[y[k]-1:ey[k], x[k]-1:ex[k], :]
                if tmp.shape[0] > 0 and tmp.shape[1] > 0 or \
                        tmp.shape[0] == 0 and tmp.shape[1] == 0:
                    tempimg[:, :, :, k] = cv2.resize(
                        tmp, (48, 48), interpolation=cv2.INTER_AREA)
                else:
                    return []
            tempimg = (tempimg-127.5)*0.0078125
            tempimg1 = np.transpose(tempimg, (3, 1, 0, 2))
            out = self._onet(tempimg1)
            out0 = np.transpose(out[0])
            out1 = np.transpose(out[1])
            out2 = np.transpose(out[2])
            score = out2[1, :]
            points = out1
            ipass = np.where(score > threshold[2])
            points = points[:, ipass[0]]
            total_boxes = np.hstack([
                total_boxes[ipass[0], 0:4].copy(),
                np.expand_dims(score[ipass].copy(), 1)
            ])
            mv = out0[:, ipass[0]]

            w = total_boxes[:, 2]-total_boxes[:, 0]+1
            h = total_boxes[:, 3]-total_boxes[:, 1]+1
            points[0:5, :] = np.tile(w, (5, 1))*points[0:5, :] + \
                np.tile(total_boxes[:, 0], (5, 1))-1
            points[5:10, :] = np.tile(h, (5, 1))*points[5:10, :] + \
                np.tile(total_boxes[:, 1], (5, 1))-1
            if total_boxes.shape[0] > 0:
                total_boxes = self._bbreg(total_boxes.copy(), np.transpose(mv))
                pick = self._nms(total_boxes.copy(), 0.7, 'Min')
                total_boxes = total_boxes[pick, :]
                points = points[:, pick]
        else:
            return []

        instances = []
        for box, pts, conf in zip(total_boxes, points, score):
            box = BoundingBox.from_absolute(
                xmin=round(box[0]),
                ymin=round(box[1]),
                xmax=round(box[2]),
                ymax=round(box[3]),
                image_width=img.shape[1],
                image_height=img.shape[0]
            )
            instances.append(
                Instance().
                set("bounding_box", box).
                set("confidence", conf).
                set("face_points", pts)
            )
        return instances
