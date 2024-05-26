// 此处变量名按照svg规范
const cell1 = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<polygon points="50,110 50,130 120,130 120,110 100,110 100,30 85,30 50,65 50,70 70,70 70,110" fill="#0000ff" />
</svg>`;

const cell2 = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<path d="M 30 60 Q 30 30, 65 30 H 95 Q 130 30, 130 60 C 130 85, 70 100, 60 110 H 130 V 130 H 30 V 115 C 30 80, 100 80, 100 60 Q 100 50, 90 50 H 70 Q 60 50, 60 60" fill="#008000"/>
</svg>`;

const cell3 = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<path d="M 30 30 H 95 Q 130 30, 130 60 Q 130 75, 115 80 Q 130 85, 130 100 Q 130 130, 95 130 H 30 V 110 H 90 Q 100 110, 100 100 T 90 90 H 60 V 70 H 90 Q 100 70, 100 60 T 90 50 H 30" fill="#ff0000"/>
</svg>`;

const cell4 = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<polygon points="55,30 30,80 30,90 90,90 90,130 120,130 120,90 130,90 130,70 120,70 120,30 90,30 90,70 65,70 85,30" fill="#000080" />
</svg>`;

const cell5 = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<path d="M 30 30 H 130 V 50 H 60 V 70 H 95 Q 130 70, 130 100 T 95 130 H 30 V 110 H 90 Q 100 110, 100 100 T 90 90 H 30" fill="#800000"/>
</svg>`;

const cell6 = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<path d="M 120 30 V 50 H 80 Q 60 50, 60 60 V 100 Q 60 110, 80 110 T 100 100 T 80 90 H 60 V 70 H 95 Q 130 70, 130 100 T 95 130 H 65 Q 30 130, 30 100 V 60 Q 30 30, 65 30" fill="#008080"/>
</svg>`;

const cell7 = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<path d="M 30 30 H 130 V 60 L 95 130 H 65 L 100 60 V 50 H 30" fill="#000000"/>
</svg>`;

const cell8 = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<path d="M 65 30 H 95 Q 130 30, 130 60 Q 130 75, 115 80 
	H 100 V 60 
	Q 100 50, 90 50 H 70 Q 60 50, 60 60 T 70 70 H 90 Q 100 70, 100 60 V 100 Q 100 90, 90 90 H 70 Q 60 90, 60 100 T 70 110 H 90 Q 100 110, 100 100 V 80 H 115 
	Q 130 85, 130 100 Q 130 130, 95 130 H 65 Q 30 130, 30 100 Q 30 85, 45 80 Q 30 75, 30 60 Q 30 30, 65 30" fill="#808080"/>
</svg>`;

const celldown = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
</svg>`;

const cellflag = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<polygon points="0,0 160,0 140,20 20,20 20,140 0,160" fill="#ffffff" />
	<polygon points="160,160 160,0 140,20 140,140 20,140 0,160" fill="#808080" />
	<rect x="20" y="20" width="120" height="120" fill="#c0c0c0" />
	<rect x="40" y="110" width="80" height="20" fill="#000000" />
	<rect x="60" y="100" width="40" height="10" fill="#000000" />
	<rect x="80" y="40" width="10" height="60" fill="#000000" />
	<path d="M 90 30 L 35 57 L 90 84" fill="#ff0000" />
</svg>`;

const cellmine = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<circle cx="85" cy="85" r="45" fill="#000000" />
	<rect x="20" y="80" width="130" height="10" />
	<rect y="20" x="80" width="10" height="130" />
	<line x1="40" y1="40" x2="130" y2="130" stroke-width="10" stroke="#000000" />
	<line x2="40" y1="40" x1="130" y2="130" stroke-width="10" stroke="#000000" />
	<circle cx="70" cy="70" r="11" fill="#ffffff" />
</svg>`;

const cellup = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<polygon points="0,0 160,0 140,20 20,20 20,140 0,160" fill="#ffffff" />
	<polygon points="160,160 160,0 140,20 140,140 20,140 0,160" fill="#808080" />
	<rect x="20" y="20" width="120" height="120" fill="#c0c0c0" />
</svg>`;

const blast = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#ff0000" />
	<circle cx="85" cy="85" r="45" fill="#000000" />
	<rect x="20" y="80" width="130" height="10" />
	<rect y="20" x="80" width="10" height="130" />
	<line x1="40" y1="40" x2="130" y2="130" stroke-width="10" stroke="#000000" />
	<line x2="40" y1="40" x1="130" y2="130" stroke-width="10" stroke="#000000" />
	<circle cx="70" cy="70" r="11" fill="#ffffff" />
</svg>`;

const falsemine = `<svg class="ms_cell" width="160" height="160" xmlns="http://www.w3.org/2000/svg">
	<rect x="0" y="0" width="160" height="160" fill="#808080" />
	<rect x="10" y="10" width="150" height="150" fill="#c0c0c0" />
	<circle cx="85" cy="85" r="45" fill="#000000" />
	<rect x="20" y="80" width="130" height="10" />
	<rect y="20" x="80" width="10" height="130" />
	<line x1="40" y1="40" x2="130" y2="130" stroke-width="10" stroke="#000000" />
	<line x2="40" y1="40" x1="130" y2="130" stroke-width="10" stroke="#000000" />
	<circle cx="70" cy="70" r="11" fill="#ffffff" />
	<polygon points="15,30 35,30 155,150 135,150" fill="#ff0000" />
	<polygon points="155,30 135,30 15,150 35,150" fill="#ff0000" />
</svg>`;

// 摆雷语法，原则上致敬扫雷网，兼顾已有的svg资源、修改部分不合理的设计
export const cells: { [key: string]: string } = {
    "1": cell1,
    "2": cell2,
    "3": cell3,
    "4": cell4,
    "5": cell5,
    "6": cell6,
    "7": cell7,
    "8": cell8,
    "0": celldown,
    "!": cellflag, // 旗
    "*": cellmine, // 白雷
    "a": cellup,
    "+": blast, // 红雷
    "x": falsemine, // 叉雷
}





