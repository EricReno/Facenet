import os
import cv2
import numpy
import random
import argparse
import onnxruntime

def parse_args():
    parser = argparse.ArgumentParser(description='Inference Face')

    parser.add_argument('--cuda', default=True, help='Use CUDA for inference.')

    parser.add_argument('--recognition_onnx', default='face.onnx', help='Path to the ONNX model file.')

    return parser.parse_args()

def setup_inference(cuda, onnx):
    providers = [('CUDAExecutionProvider', {'device_id': 0})] if cuda else [('CPUExecutionProvider', {})]
    print('Using CUDA' if cuda else 'Using CPU')
    return onnxruntime.InferenceSession(onnx, providers=providers)

def main():
    args = parse_args()

    recognition_session = setup_inference(args.cuda, args.recognition_onnx)

    images_list = []
    for folder in os.listdir('Images'):
        folder_path = os.path.join(os.getcwd(), 'Images', folder)
        for img_name in os.listdir(folder_path):
            images_list.append(os.path.join(folder_path, img_name))

    for index, image_path in enumerate(images_list):
        anchor_image = cv2.imread(image_path)

        photo1 = numpy.expand_dims(anchor_image.transpose([2, 0, 1]).astype(numpy.float32)/255., 0)

        output1 = recognition_session.run(['output'], {'input': photo1})[0]

        index_list = numpy.arange(index+5, len(images_list)).tolist()
        if len(index_list) < 2:
            break
        id3, id4 = random.sample(index_list, 2)
        indexs = [index, index+3, id3, id4]

        ## Load images and targets
        for index in indexs:
            current_image =  cv2.imread(images_list[index])

            photo2 = numpy.expand_dims(current_image.transpose([2, 0, 1]).astype(numpy.float32)/255., 0)

            output2 = recognition_session.run(['output'], {'input': photo2})[0]
            
            distance = numpy.sqrt(numpy.sum((output1 - output2) ** 2, 1))

            show_image = numpy.concatenate((anchor_image, current_image), axis=1)

            text_image = numpy.zeros((40, show_image.shape[1], 3), dtype=numpy.uint8)
            text = 'Yes' if distance < 0.77000 else 'No'
            cv2.putText(text_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
            final_image = numpy.concatenate((show_image, text_image), axis=0)

            cv2.imshow('image', final_image)

            print(final_image.shape)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

if __name__ == '__main__':
    main()